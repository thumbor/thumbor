#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from tornado.options import options, define

from thumbor.detectors import CascadeLoaderDetector
from thumbor.point import FocalPoint


define('FACE_DETECTOR_CASCADE_FILE', default='haarcascade_frontalface_alt.xml')


HAIR_OFFSET = 0.12

class Detector(CascadeLoaderDetector):

    def __init__(self, index, detectors):
        self.load_cascade_file(__file__, options.FACE_DETECTOR_CASCADE_FILE)
        super(Detector, self).__init__(index, detectors)

    def __add_hair_offset(self, top, height):
        top = max(0, top - height * HAIR_OFFSET)
        return top

    def detect(self, context):
        features = self.get_features(context)

        if features:
            for (left, top, width, height), neighbors in features:
                top = self.__add_hair_offset(top, height)
                context['focal_points'].append(FocalPoint.from_square(left, top, width, height))
        else:
            self.next(context)

