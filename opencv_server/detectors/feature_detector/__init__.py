#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import cv

from detectors import BaseDetector

class FeatureDetector(BaseDetector):

    def detect(self, width, height, mode, img_data):
        sz = (width, height)
        image = cv.CreateImageHeader(sz, cv.IPL_DEPTH_8U, 3)
        cv.SetData(image, img_data)

        gray_image = cv.CreateImage(sz, 8, 1);
        convert_mode = getattr(cv, 'CV_%s2GRAY' % mode)
        cv.CvtColor(image, gray_image, convert_mode)
        image = gray_image
        rows = sz[0]
        cols = sz[1]

        eig_image = cv.CreateMat(rows, cols, cv.CV_32FC1)
        temp_image = cv.CreateMat(rows, cols, cv.CV_32FC1)
        points = cv.GoodFeaturesToTrack(image, eig_image, temp_image, 20, 0.04, 1.0, useHarris = False)

        if points:
            return [[x, y, 1, 1] for x, y in points]

        return None
