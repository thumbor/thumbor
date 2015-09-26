#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from tornado.options import options, define

from thumbor.detectors.local_detector import CascadeLoaderDetector

define('GLASSES_DETECTOR_CASCADE_FILE', default='haarcascade_eye_tree_eyeglasses.xml')


class Detector(CascadeLoaderDetector):

    def __init__(self, context, index, detectors):
        super(Detector, self).__init__(context, index, detectors)
        self.load_cascade_file(__file__, options.GLASSES_DETECTOR_CASCADE_FILE)
