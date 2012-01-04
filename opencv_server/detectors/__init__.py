#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import join, dirname, abspath, isabs

import cv

class BaseDetector(object):

    def detect(self, context):
        raise NotImplementedError()


class CascadeLoaderDetector(BaseDetector):

    def load_cascade_file(self, module_path, cascade_file_path):
        if not hasattr(self.__class__, 'cascade'):
            if isabs(cascade_file_path):
                cascade_file = cascade_file_path
            else:
                cascade_file = join(abspath(dirname(module_path)), cascade_file_path)
            setattr(self.__class__, 'cascade', cv.Load(cascade_file))

    def get_min_size_for(self, size):
        ratio = int(min(size[0], size[1]) / 15)
        ratio = max(20, ratio)
        return (ratio, ratio)

    def get_features(self, width, height, mode, img_data):
        sz = (width, height)
        image = cv.CreateImageHeader(sz, cv.IPL_DEPTH_8U, 3)
        cv.SetData(image, img_data)

        gray = cv.CreateImage(sz, 8, 1);
        convert_mode = getattr(cv, 'CV_%s2GRAY' % mode)
        cv.CvtColor(image, gray, convert_mode)

        # min_size = (20, 20)
        min_size = self.get_min_size_for(sz)
        haar_scale = 1.2
        min_neighbors = 1

        cv.EqualizeHist(gray, gray)

        faces = cv.HaarDetectObjects(gray,
                                     self.__class__.cascade, cv.CreateMemStorage(0),
                                     haar_scale, min_neighbors,
                                     cv.CV_HAAR_DO_CANNY_PRUNING, min_size)

        faces_scaled = []

        for ((x, y, w, h), n) in faces:
            # the input to cv.HaarDetectObjects was resized, so scale the
            # bounding box of each face and convert it to two CvPoints
            pt1 = (x, y)
            pt2 = ((x + w), (y + h))
            x1 = pt1[0]
            x2 = pt2[0]
            y1 = pt1[1]
            y2 = pt2[1]
            faces_scaled.append(((x1, y1, x2-x1, y2-y1), None))

        return faces_scaled

    def detect(self, context):
        features = self.get_features(width, height, mode, img_data)

        if features:
            points = [[left, top, width, height] for (left, top, width, height), neighbors in features]
        else:
            points = []

        return points
