import imutils
import cv2

class ColorCenter:
	
	def __init__(self, low, up):
		print("ColorCenter Inizializzato")
		self.colorLower = (low, 100, 100)
		self.colorUpper = (up, 255, 255)

	def update(self, frame, frameCenter):
		# convert the frame to hsv
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

		# construct a mask for the color, then perform
		# a series of dilations and erosions to remove any small
		# blobs left in the mask
		mask = cv2.inRange(hsv, self.colorLower, self.colorUpper)
		mask = cv2.erode(mask, None, iterations=2)
		mask = cv2.dilate(mask, None, iterations=2)
		
		# find contours in the mask and initialize the current
		# (x, y) center of the ball
		cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

		# check to see if a duck was found
		if len(cnts) > 0:
			# find the largest contour in the mask, then use
			# it to compute the minimum enclosing circle 
			c = max(cnts, key=cv2.contourArea)
			((x, y), radius) = cv2.minEnclosingCircle(c)

			# return the center (x, y)-coordinates of the duck
			if radius > 10:
				return ((x,y), radius)

		# otherwise no ducks were found, so return the center of the
		# frame
		return (frameCenter, None)