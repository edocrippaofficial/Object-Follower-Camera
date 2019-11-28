import cv2

class ColorCenter:
	
	def __init__(self, lowH, lowS, lowV, upH, upS, upV):
		self.colorLower = (lowH, lowS, lowV)
		self.colorUpper = (upH, upS, upV)

	def update(self, frame, screen_centerX, screen_centerY):
		# Convert the frame to hsv
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		# Construct a mask for the color, then perform erosion and dilation to remove any blobs left in the mask
		mask = cv2.inRange(hsv, self.colorLower, self.colorUpper)
		mask = cv2.erode(mask, None, iterations=2)
		mask = cv2.dilate(mask, None, iterations=2)
		# Find contours in the mask
		contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
		if len(contours) > 0:
			# Find the largest contour in the mask, then use it to compute the minimum enclosing circle 
			c = max(contours, key=cv2.contourArea)
			(x, y), radius = cv2.minEnclosingCircle(c)
			if radius > 10:
				return x, y, radius
		# No objects found, return screen center and 0 as radius
		return screen_centerX, screen_centerY, 0