import imutils
import numpy as np
import math
import cv2
from utils.centroidtracker import CentroidTracker

# load serialized model from disk
net = cv2.dnn.readNetFromCaffe("utils/deploy.prototxt", "utils/res10_300x300_ssd_iter_140000.caffemodel")
ct = CentroidTracker(20)

class FaceCenterDnn:
	
	def __init__(self, conf):
		self.confidence = conf
		print("FaceCenterDnn Inizializzato")

	def update(self, frame, frameCenter):
		# frame dimensions
		(H, W) = frame.shape[:2]
   
		# construct a blob from the frame, pass it through the network,
		# obtain our output predictions, and initialize the list of
		# bounding box rectangles
		blob = cv2.dnn.blobFromImage(frame, 1.0, (W, H), (104.0, 177.0, 123.0))
		net.setInput(blob)
		detections = net.forward()
		rects = []

		# loop over the detections	
		objects = None
   
		for i in range(0, detections.shape[2]):
			# filter out weak detections by ensuring the predicted
			# probability is greater than a minimum threshold
			if detections[0, 0, i, 2] > self.confidence: 
				# compute the (x, y)-coordinates of the bounding box for
				# the object
				box = detections[0, 0, i, 3:7] * np.array([W, H, W, H])
				rects.append(box.astype("int"))
    
		# update our centroid tracker using the computed set of bounding
		# box rectangles
		objects = ct.update(rects)
  
		if (detections.shape[2] == 0):
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
