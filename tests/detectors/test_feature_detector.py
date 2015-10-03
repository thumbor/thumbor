#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import abspath
from unittest import TestCase
import mock

from preggy import expect

from thumbor.detectors.feature_detector import Detector as FeatureDetector
from thumbor.engines.pil import Engine as PilEngine


class FeatureDetectorTestCase(TestCase):
    def setUp(self):
        self.context = mock.Mock(request=mock.Mock(focal_points=[]))
        self.engine = PilEngine(self.context)
        self.context.modules.engine = self.engine

    def test_should_detect_multiple_points(self):
        with open(abspath('./tests/fixtures/images/no_face.jpg')) as f:
            self.engine.load(f.read(), None)

        FeatureDetector(self.context, 0, None).detect(lambda: None)
        detection_result = self.context.request.focal_points
        expect(detection_result).to_be_greater_than(1)
        expect(detection_result[0].origin).to_equal('alignment')

    def test_should_not_detect_points(self):
        with open(abspath('./tests/fixtures/images/white-block.png')) as f:
            self.engine.load(f.read(), None)

        FeatureDetector(self.context, 0, []).detect(lambda: None)
        detection_result = self.context.request.focal_points
        expect(detection_result).to_length(0)
