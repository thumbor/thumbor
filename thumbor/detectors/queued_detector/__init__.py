from pyremotecv import PyRemoteCV

from thumbor.detectors import BaseDetector

class QueuedDetector(BaseDetector):
    pyremotecv = None

    def detect(self, callback):
        if not self.pyremotecv:
            self.pyremotecv = PyRemoteCV(host=self.context.config.REDIS_QUEUE_SERVER_HOST,
                                         port=self.context.config.REDIS_QUEUE_SERVER_PORT,
                                         db=self.context.config.REDIS_QUEUE_SERVER_DB,
                                         password=self.context.config.REDIS_QUEUE_SERVER_PASSWORD)
        self.pyremotecv.async_detect('remotecv.pyres_tasks.DetectTask', 'Detect',
                args=[self.detection_type, self.context.request.image_url],
                key=self.context.request.image_url)
        self.context.prevent_result_storage = True
        callback([])
