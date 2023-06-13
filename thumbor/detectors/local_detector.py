#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from os.path import abspath, dirname, isabs, join
from typing import Dict

import numpy as np

from thumbor.detectors import BaseDetector
from thumbor.point import FocalPoint


class CascadeLoaderDetector(BaseDetector):
    def load_cascade_file(self, module_path, cascade_file_path):
        import cv2  # noqa pylint: disable=import-error,import-outside-toplevel

        if not hasattr(self.__class__, "cascade"):
            if isabs(cascade_file_path):
                cascade_file = cascade_file_path
            else:
                cascade_file = join(
                    abspath(dirname(module_path)), cascade_file_path
                )
            self.__class__.cascade = (
                cv2.CascadeClassifier(  # pylint: disable=no-member
                    cascade_file
                )
            )

    def get_min_size_for(self, size):
        ratio = int(min(size) / 15)
        ratio = max(20, ratio)

        return (ratio, ratio)

    def get_features(self):
        engine = self.context.modules.engine
        img = np.array(
            engine.convert_to_grayscale(update_image=False, alpha=False)
        )

        faces = self.__class__.cascade.detectMultiScale(
            img, 1.2, 4, minSize=self.get_min_size_for(engine.size)
        )
        faces_scaled = []

        for posx, posy, width, height in faces:
            faces_scaled.append(
                ((posx.item(), posy.item(), width.item(), height.item()), 0)
            )

        return faces_scaled

    def get_origin(self) -> str:
        return "detection"

    def get_detection_offset(
        self,
        left: int,  # pylint: disable=unused-argument
        top: int,  # pylint: disable=unused-argument
        width: int,  # pylint: disable=unused-argument
        height: int,  # pylint: disable=unused-argument
    ) -> Dict[str, int]:
        return {}

    async def detect(self):
        if not self.verify_cv():
            await self.next()

            return

        features = self.get_features()

        if not features:
            await self.next()  # pylint: disable=not-callable

        for (left, top, width, height), _ in features:
            offset = self.get_detection_offset(left, top, width, height)
            self.context.request.focal_points.append(
                FocalPoint.from_square(
                    left + offset.get("left", 0.0),
                    top + offset.get("top", 0.0),
                    width + offset.get("right", 0.0),
                    height + offset.get("bottom", 0.0),
                    origin=self.get_origin(),
                )
            )
