#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import join, dirname, abspath, isabs

try:
    import cv
except ImportError:
    import cv2.cv as cv

from thumbor.point import FocalPoint
from thumbor.detectors import BaseDetector


class CascadeLoaderDetector(BaseDetector):

    def load_cascade_file(self, module_path, cascade_file_path):
        if not hasattr(self.__class__, 'cascade'):
            if isabs(cascade_file_path):
                cascade_file = cascade_file_path
            else:
                cascade_file = join(abspath(dirname(module_path)), cascade_file_path)
            self.__class__.cascade = cv.Load(cascade_file)

    def get_min_size_for(self, size):
        ratio = int(min(size) / 15)
        ratio = max(20, ratio)
        return (ratio, ratio)

    def get_features(self):
        engine = self.context.modules.engine

        mode, converted_image = engine.convert_to_rgb()
        size = engine.size

        image = cv.CreateImageHeader(size, cv.IPL_DEPTH_8U, 3)
        cv.SetData(image, converted_image)

        gray = cv.CreateImage(size, 8, 1)
        convert_mode = getattr(cv, 'CV_%s2GRAY' % mode)
        cv.CvtColor(image, gray, convert_mode)

        min_size = self.get_min_size_for(size)
        haar_scale = 1.2
        min_neighbors = 3

        cv.EqualizeHist(gray, gray)

        faces = cv.HaarDetectObjects(
            gray,
            self.__class__.cascade, cv.CreateMemStorage(0),
            haar_scale, min_neighbors,
            cv.CV_HAAR_DO_CANNY_PRUNING, min_size)

        faces_scaled = []

        for ((x, y, w, h), n) in faces:
            # the input to cv.HaarDetectObjects was resized, so scale the
            # bounding box of each face and convert it to two CvPoints
            x2, y2 = (x + w), (y + h)
            faces_scaled.append(((x, y, x2 - x, y2 - y), n))

        return faces_scaled

    def detect(self, callback):
        features = self.get_features()

        if features:
            for square, neighbors in features:
                self.context.request.focal_points.append(FocalPoint.from_square(*square))
            callback()
        else:
            self.next(callback)
