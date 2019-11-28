from utils.centroidtracker import CentroidTracker
import numpy as np
import cv2

class FaceCenterDnn:
	
	def __init__(self, confidence):
		self.confidence = confidence
		self.net = cv2.dnn.readNetFromCaffe('utils/face_recognizer_dnn.prototxt', 'utils/face_recognizer_dnn.caffemodel')
		self.centroid_tracker = CentroidTracker(20)

	def update(self, frame, screen_centerX, screen_centerY):
		height, width = frame.shape[:2]
		# Construct a blob from the frame and pass it through the network
		blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
		self.net.setInput(blob)
		detections = self.net.forward()
		# Initialize the list of bounding box rectangles
		rects = []
		for i in range(detections.shape[2]):
			# Filter out weak detections by ensuring the predicted probability is greater than a minimum threshold
			if detections[0, 0, i, 2] > self.confidence: 
				# compute the x and y coordinates of the bounding box for the object
				box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
				rects.append(box.astype("int"))
		# Update centroid tracker using the computed set of bounding box rectangles
		objects = self.centroid_tracker.update(rects)
		# No faces found, return screen center and 0 as radius
		if detections.shape[2] == 0:
			return screen_centerX, screen_centerY, 0
		# Loop over the tracked objects and pick center of the object with lower id
		center = (screen_centerX, screen_centerY)
		min_id = 999
		if objects is not None:
			for objectID, centroid in objects.items():
				text = "ID {}".format(objectID)
				cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
				if objectID < min_id:
					min_id = objectID
					center = centroid
		x = center[0]
		y = center[1]
		radius = center[2] if len(center) > 2 else 0
		return x, y, radius