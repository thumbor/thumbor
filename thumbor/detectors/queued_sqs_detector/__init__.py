#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com


from remotecv.celery_tasks import CeleryTasks

from thumbor.detectors import BaseDetector
from thumbor.utils import logger


class Detector(BaseDetector):
    detect_task = None

    async def detect(self):
        self.context.request.prevent_result_storage = True
        try:
            if not Detector.detect_task:
                celery_tasks = CeleryTasks(
                    self.context.config.SQS_QUEUE_KEY_ID,
                    self.context.config.SQS_QUEUE_KEY_SECRET,
                    self.context.config.SQS_QUEUE_REGION,
                    None,
                )
                Detector.detect_task = celery_tasks.get_detect_task()

            Detector.detect_task.delay(
                "all",
                self.context.request.image_url,
                self.context.request.image_url,
            )
        except RuntimeError:
            self.context.request.detection_error = True
            Detector.detect_task = None
            logger.exception("Celery Error")

        # Error or not we return an empty list as detection
        # will be done later
        return []
