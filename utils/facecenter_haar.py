from utils.centroidtracker import CentroidTracker
import cv2

class FaceCenterHaar:
	
	def __init__(self):
		self.face_detector = cv2.CascadeClassifier("utils/face_recognizer_haarcascade.xml")
		self.cenroid_tracker = CentroidTracker(50)

	def update(self, frame, screen_centerX, screen_centerY):
		# Convert the frame to grayscale
		frame_grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		# Detect all faces in the input frame
		faces = self.face_detector.detectMultiScale(frame_grayscale, 1.05, 9, minSize=(30, 30))
		# Initialize the list of bounding box rectangles
		rects = []
		for (x, y, w, h) in faces:
			# compute the x and y coordinates of the bounding box for the object
			box = [x+20, y+20, x+w-20, y+h-20]
			rects.append(box)
		# Update centroid tracker using the computed set of bounding box rectangles
		objects = self.cenroid_tracker.update(rects)
 		# No faces found, return screen center and 0 as radius
		if len(faces) == 0:
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