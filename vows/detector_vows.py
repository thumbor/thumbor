#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect
from thumbor.detectors import BaseDetector

ctx = Vows.Context


def get_detector(name):
    class MockDetector:
        def __init__(self, context, index, detectors):
            self.context = context
            self.index = index
            self.detectors = detectors
            self.name = name

        def detect(self, callback):
            callback(self.name)

    return MockDetector


@Vows.batch
class BaseDetectorVows(ctx):

    class CreateInstanceVows(ctx):
        def topic(self):
            return BaseDetector("context", 1, "detectors")

        def should_not_be_null(self, topic):
            expect(topic).not_to_be_null()
            expect(topic).not_to_be_an_error()

    class DetectShouldRaise(ctx):
        @Vows.capture_error
        def topic(self):
            BaseDetector("context", 1, "detectors").detect(None)

        def should_be_an_error(self, topic):
            expect(topic).to_be_an_error()
            expect(topic).to_be_an_error_like(NotImplementedError)

    class NextVows(ctx):
        @Vows.async_topic
        def topic(self, callback):
            detector = BaseDetector("context", 0, [
                get_detector("a"),
                get_detector("b")
            ])
            return detector.next(callback)

        def should_be_detector_b(self, topic):
            expect(topic.args[0]).to_equal("b")

    class LastDetectorVows(ctx):
        @Vows.async_topic
        def topic(self, callback):
            detector = BaseDetector("context", 0, [
                get_detector("a")
            ])
            return detector.next(callback)

        def should_be_null(self, topic):
            expect(topic.args).to_length(0)
