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
        engine = context['engine']
        sz = engine.size
        mode = engine.get_image_mode()
        image = cv.CreateImageHeader(sz, cv.IPL_DEPTH_8U, 3)
        cv.SetData(image, engine.get_image_data())

        gray = cv.CreateImage(sz, 8, 1);
        convert_mode = getattr(cv, 'CV_%s2GRAY' % mode)
        cv.CvtColor(image, gray, convert_mode)

        min_size = (20, 20)
        image_scale = 1.0
        haar_scale = 1.2
        min_neighbors = 2

        if image_scale != 1.0:
            thumbnail = cv.CreateMat(int(round(image.height / image_scale, 0)), int(round(image.width / image_scale, 0)), cv.CV_8UC1)
            cv.Resize(gray, thumbnail)
            gray = thumbnail

        cv.EqualizeHist(gray, gray)

        faces = cv.HaarDetectObjects(gray,
                                     self.__class__.cascade, cv.CreateMemStorage(0),
                                     haar_scale, min_neighbors,
                                     cv.CV_HAAR_DO_CANNY_PRUNING, min_size)

        #faces = cv.HaarDetectObjects(
            #image,
            #self.__class__.cascade,
            #cv.CreateMemStorage(0),
            #scale_factor=1.1,
            #min_neighbors=3,
            #flags=cv.CV_HAAR_DO_CANNY_PRUNING,
            #min_size=(40, 40)
        #)

        faces_scaled = []

        for ((x, y, w, h), n) in faces:
            # the input to cv.HaarDetectObjects was resized, so scale the
            # bounding box of each face and convert it to two CvPoints
            pt1 = (int(x * image_scale), int(y * image_scale))
            pt2 = (int((x + w) * image_scale), int((y + h) * image_scale))
            x1 = pt1[0]
            x2 = pt2[0]
            y1 = pt1[1]
            y2 = pt2[1]
            faces_scaled.append(((x1, y1, x2-x1, y2-y1), None))

        return faces_scaled

    def detect(self, context):
        features = self.get_features(context)

        if features:
            for (left, top, width, height), neighbors in features:
                context['focal_points'].append(FocalPoint.from_square(left, top, width, height))
        else:
            self.next(context)

