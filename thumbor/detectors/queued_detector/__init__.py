from remotecv import pyres_tasks
from remotecv.unique_queue import UniqueQueue

from thumbor.detectors import BaseDetector

class QueuedDetector(BaseDetector):
    queue = UniqueQueue()

    def detect(self, callback):
        self.queue.enqueue(pyres_tasks.DetectTask, self.detection_type, self.context.request.image_url,
            self.context.request.crop['left'], self.context.request.crop['top'],
            self.context.request.crop['right'], self.context.request.crop['bottom'])
        self.context.prevent_result_storage = True
        callback([])
