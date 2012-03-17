
from thumbor.detectors import BaseDetector

class Detector(BaseDetector):
    def detect(self, callback):
        self.context.request.prevent_result_storage = True
        callback()
