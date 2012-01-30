#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from tornado.options import options, define

from thumbor.detectors.local_detector import CascadeLoaderDetector

define('PROFILE_DETECTOR_CASCADE_FILE', default='haarcascade_profileface.xml')

class Detector(CascadeLoaderDetector):

    def __init__(self, index, detectors):
        self.load_cascade_file(__file__, options.PROFILE_DETECTOR_CASCADE_FILE)
        super(Detector, self).__init__(index, detectors)
