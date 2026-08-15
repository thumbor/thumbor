# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from os.path import abspath
from unittest import mock

from tornado.testing import gen_test

import thumbor.detectors
from tests.base import DetectorTestCase
from thumbor.detectors.feature_detector import Detector as FeatureDetector


class FeatureDetectorTestCase(DetectorTestCase):
    @gen_test
    async def test_should_detect_multiple_points(self):
        with open(
            abspath("./tests/fixtures/images/no_face.jpg"), "rb"
        ) as fixture:
            self.engine.load(fixture.read(), None)

        await FeatureDetector(self.context, 0, None).detect()
        detection_result = self.context.request.focal_points
        assert len(detection_result) > 1
        assert detection_result[0].origin == "alignment"

    @gen_test
    async def test_should_detect_a_single_point(self):
        with open(
            abspath("./tests/fixtures/images/single_point.jpg"), "rb"
        ) as fixture:
            self.engine.load(fixture.read(), None)

        await FeatureDetector(self.context, 0, None).detect()
        detection_result = self.context.request.focal_points
        assert len(detection_result) == 1
        assert detection_result[0].origin == "alignment"

    @gen_test
    async def test_should_not_detect_points(self):
        with open(abspath("./tests/fixtures/images/1x1.png"), "rb") as fixture:
            self.engine.load(fixture.read(), None)

        await FeatureDetector(self.context, 0, []).detect()
        detection_result = self.context.request.focal_points
        assert len(detection_result) == 0

    @gen_test
    async def test_should_skip_if_opencv_not_found(self):
        with open(
            abspath("./tests/fixtures/images/no_face.jpg"), "rb"
        ) as fixture:
            self.engine.load(fixture.read(), None)

        with mock.patch.object(
            thumbor.detectors.BaseDetector, "verify_cv", lambda self: False
        ):
            await FeatureDetector(self.context, 0, None).detect()

        detection_result = self.context.request.focal_points
        assert len(detection_result) == 0
