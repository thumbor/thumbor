#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.detectors.local_detector import CascadeLoaderDetector


class Detector(CascadeLoaderDetector):

    def __init__(self, context, index, detectors):
        self.load_cascade_file(__file__, context.config.PROFILE_DETECTOR_CASCADE_FILE)
        super(Detector, self).__init__(context, index, detectors)
