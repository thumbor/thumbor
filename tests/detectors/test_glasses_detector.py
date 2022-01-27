#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from os.path import abspath
from unittest import mock

from preggy import expect
from tornado.testing import gen_test

import thumbor.detectors
from tests.base import DetectorTestCase
from thumbor.detectors.glasses_detector import Detector as GlassesDetector


class GlassesDetectorTestCase(DetectorTestCase):
    @gen_test
    async def test_detector_uses_proper_cascade(self):
        cascade = "./tests/fixtures/haarcascade_eye_tree_eyeglasses.xml"
        ctx = mock.Mock(
            config=mock.Mock(
                GLASSES_DETECTOR_CASCADE_FILE=abspath(cascade),
            )
        )

        detector = GlassesDetector(ctx, 1, [])
        expect(detector).not_to_be_null()

    @gen_test
    async def test_should_detect_glasses(self):
        with open(
            abspath(
                "./tests/fixtures/images/Christophe_Henner_-_June_2016.jpg"
            ),
            "rb",
        ) as fixture:
            self.engine.load(fixture.read(), None)

        self.context.config.GLASSES_DETECTOR_CASCADE_FILE = abspath(
            "./thumbor/detectors/glasses_detector/"
            "haarcascade_eye_tree_eyeglasses.xml",
        )

        if hasattr(GlassesDetector, "cascade"):
            del GlassesDetector.cascade
        await GlassesDetector(self.context, 0, []).detect()
        detection_result = self.context.request.focal_points[0]
        expect(detection_result.origin).to_equal("detection")
        expect(detection_result.x).to_be_numeric()
        expect(detection_result.y).to_be_numeric()
        expect(detection_result.width).to_be_numeric()
        expect(detection_result.height).to_be_numeric()

    @gen_test
    async def test_should_skip_if_opencv_not_found(self):
        with open(
            abspath(
                "./tests/fixtures/images/Christophe_Henner_-_June_2016.jpg"
            ),
            "rb",
        ) as fixture:
            self.engine.load(fixture.read(), None)

        self.context.config.GLASSES_DETECTOR_CASCADE_FILE = abspath(
            "./thumbor/detectors/glasses_detector/"
            "haarcascade_eye_tree_eyeglasses.xml",
        )

        if hasattr(GlassesDetector, "cascade"):
            del GlassesDetector.cascade

        with mock.patch.object(
            thumbor.detectors.BaseDetector, "verify_cv", lambda self: False
        ):
            await GlassesDetector(self.context, 0, []).detect()

        detection_result = self.context.request.focal_points
        expect(detection_result).to_length(0)
