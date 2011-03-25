#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from cStringIO import StringIO

import cv
from PIL import Image

from thumbor.detectors import BaseDetector
from thumbor.point import FocalPoint

class Detector(BaseDetector):

    def detect(self, context):
        size = context['engine'].size
        image_header = cv.CreateImageHeader(size, cv.IPL_DEPTH_8U, 3)
        cv.SetData(image_header, Image.open(StringIO(context['buffer'])).tostring())

        grayscale = cv.CreateImage(size, 8, 1)
        cv.CvtColor(image_header, grayscale, cv.CV_BGR2GRAY)
        cv.EqualizeHist(grayscale, grayscale)

        eig_image = cv.CreateMat(size[0], size[1], cv.CV_32FC1)
        temp_image = cv.CreateMat(size[0], size[1], cv.CV_32FC1)

        points = cv.GoodFeaturesToTrack(grayscale, eig_image, temp_image, 100, 0.04, 1.0, useHarris=False)

        if points:
            for x, y in points:
                context['focal_points'].append(FocalPoint(x, y, 1))
        else:
            self.next(context)
