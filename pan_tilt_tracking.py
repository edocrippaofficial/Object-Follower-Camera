from multiprocessing import Manager
from multiprocessing import Process
from imutils.video import VideoStream
from utils.colorpicker import ColorPicker
from utils.colorcenter import ColorCenter
from utils.facecenter_dnn import FaceCenterDnn
from utils.facecenter_haar import FaceCenterHaar
from utils.pid import PID
import serial.tools.list_ports as arduino_ports
import serial
import argparse
import struct
import time
import sys
import cv2

# PID values
panP = 0.5
panI = 0.03
panD = 0.01

tiltP = 0.6
tiltI = 0.04
tiltD = 0.01

stream = None
centerX = 0
centerY = 0

def track(object_centerX, object_centerY):
    writer = cv2.VideoWriter('video.avi', cv2.VideoWriter_fourcc(*'XVID'), 30, (centerX*2, centerY*2))
    while True:
        # Read the next frame from video stream
        frame = stream.read()
        frame = cv2.flip(frame, 1)
        # Find the object_centerect location (x, y, radius) in the stream
        object_centerX.value, object_centerY.value, radius = object_center.update(frame, centerX, centerY)
        # Draw the bounding circle on the frame
        if radius > 0:
            cv2.circle(frame, (int(object_centerX.value), int(object_centerY.value)), int(radius), (0, 255, 255), 2)
        # Display frame
        cv2.imshow("Pan-Tilt Tracking", frame)
        writer.write(frame)
        # End process when key 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            stream.stop()
            writer.release()
            break

def pid(output, coord, object_center):
    # Get the right values and initialize PID
    if coord == 'pan':
        pid = PID(panP, panI, panD)
        screen_center = centerX
    else:
        pid = PID(tiltP, tiltI, tiltD)
        screen_center = centerY
    pid.initialize()
    while True:
        # Calculate the error
        error = screen_center - object_center.value
        # If error is 0 then object is in center or is not detected, so re-initialize PID
        if abs(error) < screen_center / 10:
            pid.initialize()
            output.value = 0
        else:
            output.value = pid.update(error)
            time.sleep(0.01)

def serial_comm(pan, tilt):
    pan_prev = -1
    tilt_prev = -1
    while True:
        pan_value = clamp(int(pan.value))
        tilt_value = clamp(int(-tilt.value))
        if arduino and (pan_value != pan_prev or tilt_value != tilt_prev):
            pan_prev = pan_value
            tilt_prev = tilt_value
            print("Pan: " + str(pan_value) + " | Tilt: " + str(tilt_value))
            arduino.write(struct.pack(">b", pan_value))
            arduino.write(struct.pack(">b", tilt_value))

def clamp(value):
    return max(-128, min(value, 127))

if __name__ == "__main__":

    # Construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--face", help="track a human face", action='store_true')
    group.add_argument("-c", "--color", help="track selected color (need lower and upper HSV values)", nargs=2, type=int, metavar=('low','up'))
    group.add_argument("-p", "--pick", help="track a picked color", action='store_true')
    ap.add_argument("-na", help="run script without Arduino connected", action='store_false')
    ap.add_argument("--dnn", help="use a deep neural network instead of haar cascades for tracking the face", action='store_true')
    ap.add_argument("--camera", help="select the camera source", default=2, type=int, metavar=("src"))
    args = vars(ap.parse_args())

    # Initialize object_center according to tracker choice
    if (args["pick"]):
        lower, upper = ColorPicker().pick(args["camera"])
        print("Tracking [H S W]: lower " + str(lower) + " | upper " + str(upper))
        object_center = ColorCenter(lower[0], lower[1], lower[2], upper[0], upper[1], upper[2])
    if (args["color"] is not None):
        print("Tracking [H S W]: lower [" + str(args["color"][0]) + " 100 100] | upper [" + str(args["color"][1]) + " 255 255]")
        object_center = ColorCenter(args["color"][0], 100, 100, args["color"][1], 255, 255)
    if (args["face"]):
        if (args["dnn"]):
            print("Tracking face - with deep neural network")
            object_center = FaceCenterDnn(0.8)
        else:
            print("Tracking face - with haar cascade")
            object_center = FaceCenterHaar()
     
    # Initialize arduino connection if required
    arduino = None
    if args["na"]:
        ports = [p.device for p in arduino_ports.comports() if 'Arduino' in p.description]
        if len(ports) > 0:
            arduino = serial.Serial(ports[0], 9600)
            print("Arduino connected!")
            time.sleep(1)
        else:
            print("No Arduino connected.\nExiting...")
            sys.exit()

    # Start the video stream
    stream = VideoStream(src=args["camera"]).start()
    # Get centerX and centertY from stream resolution
    frame = stream.read()
    (height, width) = frame.shape[:2]
    centerX = width // 2
    centerY = height // 2

    # Start a manager for managing process-safe variables
    with Manager() as manager:
        object_centerX = manager.Value("i", 0)
        object_centerY = manager.Value("i", 0)
        pan = manager.Value("i", 0)
        tilt = manager.Value("i", 0)
        # Create processes for pan PID, tilt PID and serial communication
        processPanPID = Process(target=pid, args=(pan, 'pan', object_centerX))
        processTiltPID = Process(target=pid, args=(tilt, 'tilt', object_centerY))
        processSerialComm = Process(target=serial_comm, args=(pan, tilt))
        # Start processes
        processPanPID.start()
        processTiltPID.start()
        processSerialComm.start()
        # Start object tracking
        track(object_centerX, object_centerY)
        # Track ended, terminate the other processes
        processPanPID.terminate()
        processTiltPID.terminate()
        processSerialComm.terminate()       