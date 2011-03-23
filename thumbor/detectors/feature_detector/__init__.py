#!/usr/bin/env python
#-*- coding: utf8 -*-

from os.path import join, dirname, abspath
from cStringIO import StringIO

import cv
from PIL import Image
from tornado.options import options

from thumbor.detectors import BaseDetector

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
            x, y = self.get_center_of_mass(points)

            return x/size[0], y/size[1]
        else:
            self.next(context)

    def get_center_of_mass(self, points):
        x = reduce(lambda acc, point: acc + point[0], points, 0) / len(points)
        y = reduce(lambda acc, point: acc + point[1], points, 0) / len(points)

        return x, y