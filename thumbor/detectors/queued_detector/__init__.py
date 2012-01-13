from remotecv import pyres_tasks
from remotecv.unique_queue import UniqueQueue

from thumbor.detectors import BaseDetector

class QueuedDetector(BaseDetector):
    queue = UniqueQueue()

    def detect(self, callback):
        engine = self.context.modules.engine
        self.queue.enqueue_unique(pyres_tasks.DetectTask,
                args=[self.detection_type, self.context.request.image_url],
                key=self.context.request.image_url)
        self.context.prevent_result_storage = True
        callback([])
