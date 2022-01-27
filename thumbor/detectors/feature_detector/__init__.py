#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

try:
    import numpy as np
    import cv2
except ImportError:
    pass

from thumbor.detectors import BaseDetector
from thumbor.point import FocalPoint
from thumbor.utils import logger


class Detector(BaseDetector):
    async def detect(self):
        if not self.verify_cv():
            await self.next()

            return

        engine = self.context.modules.engine
        try:
            img = np.array(
                engine.convert_to_grayscale(update_image=False, alpha=False)
            )
        except Exception as error:
            logger.exception(error)
            logger.warning(
                "Error during feature detection; skipping to next detector"
            )

            return await self.next()  # pylint: disable=not-callable

        points = cv2.goodFeaturesToTrack(  # pylint: disable=no-member
            img,
            maxCorners=20,
            qualityLevel=0.04,
            minDistance=1.0,
            useHarrisDetector=False,
        )

        if points is not None:
            for point in points:
                x_pos, y_pos = point.ravel()
                self.context.request.focal_points.append(
                    FocalPoint(x_pos.item(), y_pos.item(), 1)
                )

            return

        await self.next()  # pylint: disable=not-callable
