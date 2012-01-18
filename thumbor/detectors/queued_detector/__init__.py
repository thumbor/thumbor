from pyremotecv import PyRemoteCV

from thumbor.detectors import BaseDetector

class QueuedDetector(BaseDetector):

    def detect(self, callback):
        PyRemoteCV.async_detect('remotecv.pyres_tasks.DetectTask', 'Detect',
                args=[self.detection_type, self.context.request.image_url],
                key=self.context.request.image_url)
        self.context.prevent_result_storage = True
        callback([])
