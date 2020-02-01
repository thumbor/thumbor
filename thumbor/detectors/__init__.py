#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com


class BaseDetector:
    def __init__(self, context, index, detectors):
        self.context = context
        self.index = index
        self.detectors = detectors

    async def detect(self):
        raise NotImplementedError()

    async def next(self):
        if self.index > len(self.detectors) - 2:
            return

        next_detector = self.detectors[self.index + 1](
            self.context, self.index + 1, self.detectors
        )
        await next_detector.detect()
