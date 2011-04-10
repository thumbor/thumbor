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
