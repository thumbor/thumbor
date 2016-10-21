#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com


from redis import Redis, RedisError
from remotecv.unique_queue import UniqueQueue

from thumbor.detectors import BaseDetector
from thumbor.utils import logger


class QueuedDetector(BaseDetector):
    queue = None
    detection_type = 'all'

    def detect(self, callback):
        self.context.request.prevent_result_storage = True
        try:
            if not QueuedDetector.queue:
                redis = Redis(host=self.context.config.REDIS_QUEUE_SERVER_HOST,
                              port=self.context.config.REDIS_QUEUE_SERVER_PORT,
                              db=self.context.config.REDIS_QUEUE_SERVER_DB,
                              password=self.context.config.REDIS_QUEUE_SERVER_PASSWORD)
                QueuedDetector.queue = UniqueQueue(server=redis)

            QueuedDetector.queue.enqueue_unique_from_string(
                'remotecv.pyres_tasks.DetectTask', 'Detect',
                args=[self.detection_type, self.context.request.image_url],
                key=self.context.request.image_url
            )
        except RedisError:
            self.context.request.detection_error = True
            QueuedDetector.queue = None
            logger.exception('Redis Error')
        finally:
            callback([])
