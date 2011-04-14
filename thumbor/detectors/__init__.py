#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import join, dirname, abspath, isabs

import cv

from thumbor.point import FocalPoint


class BaseDetector(object):

    def __init__(self, index, detectors):
        self.index = index
        self.detectors = detectors

    def detect(self, context):
        raise NotImplementedError()

    def next(self, context):
        if self.index >= len(self.detectors) - 1:
            return

        next_detector = self.detectors[self.index + 1](self.index + 1, context)
        return next_detector.detect(context)


class CascadeLoaderDetector(BaseDetector):

    def load_cascade_file(self, module_path, cascade_file_path):
        if not hasattr(self.__class__, 'cascade'):
            if isabs(cascade_file_path):
                cascade_file = cascade_file_path
            else:
                cascade_file = join(abspath(dirname(module_path)), cascade_file_path)
            setattr(self.__class__, 'cascade', cv.Load(cascade_file))

    def get_features(self, context):
        image = cv.LoadImageM(context['file'], cv.CV_LOAD_IMAGE_GRAYSCALE)

        cv.EqualizeHist(image, image)

        haar_scale = 1.1
        min_neighbors = 3
        haar_flags = cv.CV_HAAR_DO_CANNY_PRUNING
        min_size = (20, 20)
        faces = cv.HaarDetectObjects(image, self.__class__.cascade, cv.CreateMemStorage(0),
                                     haar_scale, min_neighbors, haar_flags, min_size)
        return faces

    def detect(self, context):
        features = self.get_features(context)

        if features:
            for (left, top, width, height), neighbors in features:
                context['focal_points'].append(FocalPoint.from_square(left, top, width, height))
        else:
            self.next(context)
