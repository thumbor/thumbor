from remotecv.unique_queue import UniqueQueue

from thumbor.detectors import BaseDetector

class QueuedDetector(BaseDetector):
    queue = UniqueQueue()

    def detect(self, callback):
        engine = self.context.modules.engine
        self.queue.enqueue_unique_from_string('remotecv.pyres_tasks.DetectTask', 'Detect',
                args=[self.detection_type, self.context.request.image_url],
                key=self.context.request.image_url)
        self.context.prevent_result_storage = True
        callback([])
