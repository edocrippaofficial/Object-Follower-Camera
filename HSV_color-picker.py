import cv2
import numpy as np
import sys
from imutils.video import VideoStream
import time


image_hsv = None
image_bgr = None
pixel = (0,0,0) #RANDOM DEFAULT VALUE

def nothing(x):
    pass

def get_frame():
    # start the video stream and wait for the camera to warm up
    vs = VideoStream(src=2).start()
    time.sleep(2.0)
    while True:
        # grab the frame from the threaded video stream
        frame = vs.read()
        frame = cv2.flip(frame, 1)
        # display the frame to the screen
        cv2.imshow("Color Picker", frame)
        # wait enter key
        key = cv2.waitKey(1) & 0xFF
        if key == ord("f"):
            return frame

def pick_color(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        pixel = image_bgr[y,x] 
        blue = pixel[0]
        green = pixel[1]
        red = pixel[2]
        cv2.namedWindow('mask')
        cv2.createTrackbar('R','mask',0,255,nothing)
        cv2.createTrackbar('G','mask',0,255,nothing)
        cv2.createTrackbar('B','mask',0,255,nothing)
        cv2.setTrackbarPos('R', 'mask', red)
        cv2.setTrackbarPos('G', 'mask', green)
        cv2.setTrackbarPos('B', 'mask', blue)
        while True:  
            color = np.uint8([[[blue, green, red]]])
            hsv_color = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)
            
            hue = hsv_color[0][0][0]

            upper =  np.array([hue + 10, 255, 255])
            lower =  np.array([hue - 10, 100, 100])

            image_mask = cv2.inRange(image_hsv,lower,upper)
            cv2.imshow("mask",image_mask)
            
            red = cv2.getTrackbarPos('R','mask')
            green = cv2.getTrackbarPos('G','mask')
            blue = cv2.getTrackbarPos('B','mask')
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            
        print(lower, upper)
        print("RGB: " + str(red) + " " + str(green) + " " + str(blue))

def main():

    global image_hsv, image_bgr, pixel

    image_src = get_frame()
    cv2.imshow("BGR",image_src)
    
    image_bgr = image_src
    
    image_hsv = cv2.cvtColor(image_src,cv2.COLOR_BGR2HSV)  
      
    cv2.setMouseCallback("BGR", pick_color)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__=='__main__':
    main()
