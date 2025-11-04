import cv2
import time
from config import CONFIG


class FaceDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.last_seen = None


    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        if len(faces) > 0:
            self.last_seen = time.time()
        return faces


    def face_timed_out(self):
        if self.last_seen is None:
            return False
        return (time.time() - self.last_seen) > CONFIG.FACE_DETECTION_TIMEOUT