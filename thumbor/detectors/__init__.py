#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

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
        
