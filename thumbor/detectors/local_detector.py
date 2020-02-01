#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from os.path import abspath, dirname, isabs, join

import cv2
import numpy as np

from thumbor.detectors import BaseDetector
from thumbor.point import FocalPoint


class CascadeLoaderDetector(BaseDetector):
    def load_cascade_file(self, module_path, cascade_file_path):
        if not hasattr(self.__class__, "cascade"):
            if isabs(cascade_file_path):
                cascade_file = cascade_file_path
            else:
                cascade_file = join(abspath(dirname(module_path)), cascade_file_path)
            self.__class__.cascade = cv2.CascadeClassifier(  # pylint: disable=no-member
                cascade_file
            )

    def get_min_size_for(self, size):
        ratio = int(min(size) / 15)
        ratio = max(20, ratio)
        return (ratio, ratio)

    def get_features(self):
        engine = self.context.modules.engine
        img = np.array(engine.convert_to_grayscale(update_image=False, alpha=False))

        faces = self.__class__.cascade.detectMultiScale(
            img, 1.2, 4, minSize=self.get_min_size_for(engine.size)
        )
        faces_scaled = []

        for (posx, posy, width, height) in faces:
            faces_scaled.append(
                ((posx.item(), posy.item(), width.item(), height.item()), 0)
            )

        return faces_scaled

    async def detect(self):
        features = self.get_features()

        if features:
            for square, _ in features:
                self.context.request.focal_points.append(
                    FocalPoint.from_square(*square)
                )
        else:
            await self.next()
