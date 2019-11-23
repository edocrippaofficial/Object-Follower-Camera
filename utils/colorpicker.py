from imutils.video import VideoStream
import numpy as np
import cv2

class ColorPicker():
    
    def __init__(self):
        self.lower = 0
        self.upper = 0
        self.image_bgr = None
        self.clicked = False
        self.window_pick = "Click on the desired color (press SPACE to pause)"
        self.window_mask = "Press ENTER when done"

    def pick(self, camera_src):
        # Start video stream
        stream = VideoStream(src=camera_src).start()
        pause = False
        cv2.imshow(self.window_pick, stream.read())
        # Execute method handle_click when a click is detected
        cv2.setMouseCallback(self.window_pick, self.handle_click)
        # Loops until a click is detected
        while not self.clicked:
            if not pause:
                self.image_bgr = stream.read()
                self.image_bgr = cv2.flip(self.image_bgr, 1)
                cv2.imshow(self.window_pick, self.image_bgr)
            # Toggle pause state when spacebar is pressed
            if cv2.waitKey(1) & 0xFF == ord(' '):
                pause = not pause
        # Destroy windows and release resources
        cv2.destroyAllWindows()
        stream.stop()
        return self.lower, self.upper
        
    def handle_click(self, event, x, y, flags, param):
        # Left click
        if event == cv2.EVENT_LBUTTONDOWN:
            self.clicked = True
            # Convert the stored image to HSV and take Hue
            image_hsv = cv2.cvtColor(self.image_bgr, cv2.COLOR_BGR2HSV)
            hue = image_hsv[y, x, 0]
            cv2.imshow(self.window_mask, image_hsv)
            # Hue trackbar
            cv2.createTrackbar('Color', self.window_mask, 0, 255, lambda x:x)
            cv2.setTrackbarPos('Color', self.window_mask, hue)
            # Saturation and value trackbar
            cv2.createTrackbar('Tolerance', self.window_mask, 0, 255, lambda x:x)           
            cv2.setTrackbarPos('Tolerance', self.window_mask, 205)
            while True: 
                hue = cv2.getTrackbarPos('Color', self.window_mask)
                tol = cv2.getTrackbarPos('Tolerance', self.window_mask)
                self.lower = (hue-10, 255-tol, 255-tol)
                self.upper = (hue+10, 255, 255)
                # Create mask for selected color
                mask = cv2.inRange(image_hsv, self.lower, self.upper)
                # Apply mask to original image
                image_mask = cv2.bitwise_or(self.image_bgr, (0, 0, 0), mask=mask)
                cv2.imshow(self.window_mask, image_mask)
                # Wait for enter key
                if cv2.waitKey(1) & 0xFF == ord("\r"):
                    # Print press any key message, needed because otherwise windows would not close
                    height, width, _ = self.image_bgr.shape
                    msg = np.zeros((height, width, 3), np.uint8)
                    cv2.putText(msg, 'Press any key to continue...', (int(width/6), int(height/2)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.imshow(self.window_mask, msg)
                    return

if __name__ == "__main__":
    lower, upper = ColorPicker().pick(0)
    print("Picked [H S W]: lower " + str(lower) + " | upper " + str(upper))