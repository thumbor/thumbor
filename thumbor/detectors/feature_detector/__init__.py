#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import cv

from thumbor.detectors import BaseDetector
from thumbor.point import FocalPoint


class Detector(BaseDetector):

    def detect(self, context):
        img = cv.LoadImageM(context['file'], cv.CV_LOAD_IMAGE_GRAYSCALE)
        eig_image = cv.CreateMat(img.rows, img.cols, cv.CV_32FC1)
        temp_image = cv.CreateMat(img.rows, img.cols, cv.CV_32FC1)
        points = cv.GoodFeaturesToTrack(img, eig_image, temp_image, 20, 0.04, 1.0, useHarris = False)

        if points:
            for x, y in points:
                context['focal_points'].append(FocalPoint(x, y, 1))
        else:
            self.next(context)
