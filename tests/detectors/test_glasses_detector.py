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

from thumbor.detectors.glasses_detector import Detector as GlassesDetector


class GlassesDetectorTestCase(TestCase):
    def test_detector_uses_proper_cascade(self):
        cascade = './tests/fixtures/haarcascade_eye_tree_eyeglasses.xml'
        ctx = mock.Mock(
            config=mock.Mock(
                GLASSES_DETECTOR_CASCADE_FILE=abspath(cascade),
            )
        )

        detector = GlassesDetector(ctx, 1, [])
        expect(detector).not_to_be_null()
