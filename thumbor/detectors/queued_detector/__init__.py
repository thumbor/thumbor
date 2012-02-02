import traceback

from pyremotecv import PyRemoteCV
from redis import RedisError

from thumbor.detectors import BaseDetector
from thumbor.utils import logger

class QueuedDetector(BaseDetector):
    pyremotecv = None

    def detect(self, callback):
        self.context.prevent_result_storage = True
        try:
            if not self.pyremotecv:
                self.pyremotecv = PyRemoteCV(host=self.context.config.REDIS_QUEUE_SERVER_HOST,
                                             port=self.context.config.REDIS_QUEUE_SERVER_PORT,
                                             db=self.context.config.REDIS_QUEUE_SERVER_DB,
                                             password=self.context.config.REDIS_QUEUE_SERVER_PASSWORD)

            self.pyremotecv.async_detect('remotecv.pyres_tasks.DetectTask', 'Detect',
                    args=[self.detection_type, self.context.request.image_url],
                    key=self.context.request.image_url)
        except RedisError:
            self.context.request.detection_error = True
            logger.error(traceback.format_exc())
        finally:
            callback([])
