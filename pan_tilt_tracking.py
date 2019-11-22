from multiprocessing import Manager
from multiprocessing import Process
from imutils.video import VideoStream
from utils.duckcenter import DuckCenter
from utils.colorcenter import ColorCenter
from utils.facecenter_dnn import FaceCenterDnn
from utils.facecenter_haar import FaceCenterHaar
from utils.pid import PID
import serial
import argparse
import serial.tools.list_ports as arduino_ports
import struct
import time
import sys
import cv2

# PID values
panP_value = 0.03
panI_value = 0.005
panD_value = 0.02

tiltP_value = 0.03
tiltI_value = 0.005
tiltD_value = 0.02

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
group = ap.add_mutually_exclusive_group(required=True)
group.add_argument("--duck", help="track a duck", action='store_true')
group.add_argument("--face", help="track a human face", action='store_true')
group.add_argument("--color", help="track selected color (need lower and upper HSV values)", nargs=2, type=int, metavar=('low','up'))
ap.add_argument("-na", help="run script without Arduino connected", action='store_true')
ap.add_argument("--dnn", help="use a deep neural network instead of haar cascades for tracking the face (useless for the duck)", action='store_true')
args = vars(ap.parse_args())
print(args)

# Tracker choice
if (args["duck"]):
    obj = DuckCenter()
if (args["color"] is not None):
    obj = ColorCenter(args["color"][0], args["color"][1])
if (args["face"]):
    if (args["dnn"]):
        obj = FaceCenterDnn(0.8)
    else:
        obj = FaceCenterHaar()
 
# Arduino connection
arduino = None
if not args["na"]:
    ports = [p.device for p in arduino_ports.comports() if 'Arduino' in p.description]
    if len(ports) > 0:
        arduino = serial.Serial(ports[0], 9600)
        print("Arduino connected!")
        time.sleep(1)
    else:
        print("No Arduino connected.\nExiting...")
        sys.exit()


def obj_center(objX, objY, centerX, centerY):
	# start the video stream and wait for the camera to warm up
	vs = VideoStream(src=2).start()
	time.sleep(2.0)

	while True:
		# grab the frame from the threaded video stream
		frame = vs.read()
		frame = cv2.flip(frame, 1)

		# calculate the center of the frame as this is where we will
		# try to keep the object
		(H, W) = frame.shape[:2]
		centerX.value = W // 2
		centerY.value = H // 2

		# find the object's location
		objectLoc = obj.update(frame, (centerX.value, centerY.value))
		((objX.value, objY.value), rad) = objectLoc

		# extract the bounding box and draw it
		if rad is not None:
			cv2.circle(frame, (int(objX.value), int(objY.value)), int(rad), (0, 255, 255), 2)

		# display the frame to the screen
		cv2.imshow("Pan-Tilt Duck Tracking", frame)

		# force exit from webcam process
		key = cv2.waitKey(1) & 0xFF
		if key == ord("q"):
			sys.exit()

def pid_process(output, p, i, d, objCoord, centerCoord):
	# create a PID and initialize it
	p = PID(p.value, i.value, d.value)
	p.initialize()
 
	while True:
		# calculate the error
		error = centerCoord.value - objCoord.value
		# update the value
		output.value = p.update(error)

def set_motors(pan, tilt):
    while True:
        print("Pan: " + str(limit_value(int(pan.value))) + " | Tilt: " + str(limit_value(int(-tilt.value))))
        if arduino:
            arduino.write(struct.pack(">b", limit_value(int(pan.value))))
            arduino.write(struct.pack(">b", limit_value(int(-tilt.value))))
        
        time.sleep(0.2)

def limit_value(value):
    return max(-128, min(value, 127))

# check to see if this is the main body of execution
if __name__ == "__main__":

	# start a manager for managing process-safe variables
	with Manager() as manager:

		# set integer values for the object center (x, y)-coordinates
		centerX = manager.Value("i", 0)
		centerY = manager.Value("i", 0)

		# set integer values for the object's (x, y)-coordinates
		objX = manager.Value("i", 0)
		objY = manager.Value("i", 0)

		# pan and tilt values will be managed by independed PIDs
		pan = manager.Value("i", 0)
		tlt = manager.Value("i", 0)

		# set PID values for panning
		panP = manager.Value("f", panP_value)
		panI = manager.Value("f", panI_value)
		panD = manager.Value("f", panD_value)

		# set PID values for tilting
		tiltP = manager.Value("f", tiltP_value)
		tiltI = manager.Value("f", tiltI_value)
		tiltD = manager.Value("f", tiltD_value)

		# we have 4 independent processes
		# 1. objectCenter  - finds/localizes the object
		# 2. panning       - PID control loop determines panning velocity
		# 3. tilting       - PID control loop determines tilting velocity
		# 4. setMotors     - drives the motors to proper speed based
		#                    on PID feedback to keep object in center
		processObjectCenter = Process(target=obj_center,
			args=(objX, objY, centerX, centerY))
		processPanning = Process(target=pid_process,
			args=(pan, panP, panI, panD, objX, centerX))
		processTilting = Process(target=pid_process,
			args=(tlt, tiltP, tiltI, tiltD, objY, centerY))
		processSetMotors = Process(target=set_motors, args=(pan, tlt))

		# start all 4 processes
		processObjectCenter.start()
		processPanning.start()
		processTilting.start()
		processSetMotors.start()

		# wait until camera process exits, then terminate all other
		# processes and exit from the program
		processObjectCenter.join()
		processPanning.terminate()
		processTilting.terminate()
		processSetMotors.terminate()
  
		