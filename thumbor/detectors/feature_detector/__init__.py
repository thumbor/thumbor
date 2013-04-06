#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

try:
    import cv
except ImportError:
    import cv2.cv as cv

from thumbor.detectors import BaseDetector
from thumbor.point import FocalPoint


class Detector(BaseDetector):

    def detect(self, callback):
        engine = self.context.modules.engine
        sz = engine.size
        image = cv.CreateImageHeader(sz, cv.IPL_DEPTH_8U, 3)

        image_mode, image_data = engine.convert_to_rgb()
        cv.SetData(image, image_data)

        gray_image = cv.CreateImage(engine.size, 8, 1);
        convert_mode = getattr(cv, 'CV_%s2GRAY' % image_mode)
        cv.CvtColor(image, gray_image, convert_mode)
        image = gray_image
        rows = sz[0]
        cols = sz[1]

        eig_image = cv.CreateMat(rows, cols, cv.CV_32FC1)
        temp_image = cv.CreateMat(rows, cols, cv.CV_32FC1)
        points = cv.GoodFeaturesToTrack(image, eig_image, temp_image, 20, 0.04, 1.0, useHarris = False)

        if points:
            for x, y in points:
                self.context.request.focal_points.append(FocalPoint(x, y, 1))
            callback()
        else:
            self.next(callback)
