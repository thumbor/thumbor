#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.utils import logger

try:
    import cv2  # noqa
    import numpy as np  # noqa

    CV_AVAILABLE = True
except ImportError:
    CV_AVAILABLE = False


class BaseDetector:
    def __init__(self, context, index, detectors):
        self.context = context
        self.index = index
        self.detectors = detectors

    def verify_cv(self) -> bool:
        if CV_AVAILABLE:
            return True

        logger.error(
            "OpenCV (cv2) is not available for thumbor. "
            "thumbor.detectors.local_detector.CascadeLoaderDetector "
            "can't be executed. Skipping..."
        )

        return False

    async def detect(self):
        raise NotImplementedError()

    async def next(self):
        if not self.detectors or self.index > len(self.detectors) - 2:
            return

        next_detector = self.detectors[self.index + 1](
            self.context, self.index + 1, self.detectors
        )
        await next_detector.detect()
