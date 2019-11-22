import imutils
import numpy as np
import math
import cv2
from utils.centroidtracker import CentroidTracker


# load OpenCV's Haar cascade face detector
detector = cv2.CascadeClassifier("utils/haarcascade_frontalface_default.xml")
ct = CentroidTracker(50)

class FaceCenterHaar:
	
	def __init__(self):
		print("FaceCenterHaar Inizializzato")

	def update(self, frame, frameCenter):
		# convert the frame to grayscale
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		# detect all faces in the input frame
		faces = detector.detectMultiScale(gray, scaleFactor=1.05,
			minNeighbors=9, minSize=(30, 30),
			flags=cv2.CASCADE_SCALE_IMAGE)

		# loop over the detections			
		objects = None
		rects = []
  
		for (x, y, w, h) in faces:
			# compute the (x, y)-coordinates of the bounding box for
			# the object
			box = [x+10, y+10, x+w-10, y+h-10]
			rects.append(box)

		# update our centroid tracker using the computed set of bounding
		# box rectangles
		objects = ct.update(rects)
    
		if (len(faces) == 0):
			return (frameCenter, None)
    
		# loop over the tracked objects
		older_cent = frameCenter
		min_id = 999
		if objects is not None:
			for (objectID, centroid) in objects.items():
				if (objectID < min_id):
					min_id = objectID
					older_cent = centroid

		x = older_cent[0]
		y = older_cent[1]
  
		if objects is not None:
			for (objectID, centroid) in objects.items():
				# draw both the ID of the object and the centroid of the
				# object on the output frame
				text = "ID {}".format(objectID)
				cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
					cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

		try:
			radius = older_cent[2]
		except:
			radius = 0

		# return the center (x, y)-coordinates of the face
		if radius > 10:
			return ((x,y), radius)
		else:
			return (frameCenter, None)
