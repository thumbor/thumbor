#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com


class BaseDetector(object):

    def __init__(self, context, index, detectors):
        self.context = context
        self.index = index
        self.detectors = detectors

    def detect(self, callback):
        raise NotImplementedError()

    def next(self, callback):
        if self.index > len(self.detectors) - 2:
            callback()
            return

        next_detector = self.detectors[self.index + 1](self.context, self.index + 1, self.detectors)
        next_detector.detect(callback)
