
from thumbor.detectors import BaseDetector

class Detector(BaseDetector):
    def detect(self, callback):
        self.context.request.detection_error = True
        callback()
