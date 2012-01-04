#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from detectors import CascadeLoaderDetector

HAIR_OFFSET = 0.12

class FaceDetector(CascadeLoaderDetector):

    def __init__(self):
        self.load_cascade_file(__file__, 'haarcascade_frontalface_alt.xml')

    def __add_hair_offset(self, top, height):
        top = max(0, top - height * HAIR_OFFSET)
        return top

    def detect(self, width, height, mode, img_data):
        features = self.get_features(width, height, mode, img_data)

        points = []
        if features:
            for (left, top, width, height), neighbors in features:
                top = self.__add_hair_offset(top, height)
                points.append([left, top, width, height])

        return points
