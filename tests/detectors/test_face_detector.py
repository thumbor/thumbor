#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from os.path import abspath
from unittest.mock import patch

from preggy import expect
from tornado.testing import gen_test

import thumbor.detectors
from tests.base import DetectorTestCase
from thumbor.detectors.face_detector import Detector as FaceDetector


class FaceDetectorTestCase(DetectorTestCase):
    @gen_test
    async def test_should_detect_one_face(self):
        with open(
            abspath(
                "./tests/fixtures/images/Giunchedi%2C_Filippo_January_2015_01.jpg"
            ),
            "rb",
        ) as fixture:
            self.engine.load(fixture.read(), None)

        for i, detector in enumerate(
            [
                "./thumbor/detectors/face_detector/"
                "haarcascade_frontalface_default.xml",
                "./thumbor/detectors/face_detector/haarcascade_frontalface_alt.xml",
                "./thumbor/detectors/face_detector/haarcascade_frontalface_alt2.xml",
                "./thumbor/detectors/face_detector/"
                "haarcascade_frontalface_alt_tree.xml",
            ]
        ):
            self.context.config.FACE_DETECTOR_CASCADE_FILE = abspath(detector)

            if hasattr(FaceDetector, "cascade"):
                del FaceDetector.cascade
            await FaceDetector(self.context, 0, None).detect()
            detection_result = self.context.request.focal_points[i]
            expect(detection_result.origin).to_equal("Face Detection")
            expect(detection_result.x).to_be_numeric()
            expect(detection_result.y).to_be_numeric()
            expect(detection_result.width).to_be_numeric()
            expect(detection_result.height).to_be_numeric()

    @gen_test
    async def test_should_skip_if_opencv_not_found(self):
        with open(
            abspath(
                "./tests/fixtures/images/Giunchedi%2C_Filippo_January_2015_01.jpg"
            ),
            "rb",
        ) as fixture:
            # ARRANGE
            self.engine.load(fixture.read(), None)
        cascade = "./thumbor/detectors/face_detector/haarcascade_frontalface_default.xml"
        self.context.config.FACE_DETECTOR_CASCADE_FILE = abspath(cascade)

        with patch.object(
            thumbor.detectors.BaseDetector, "verify_cv", lambda self: False
        ):
            if hasattr(FaceDetector, "cascade"):
                del FaceDetector.cascade

            # ACT
            await FaceDetector(self.context, 0, None).detect()

            # ASSERT
            detection_result = self.context.request.focal_points
            expect(detection_result).to_length(0)

    @gen_test
    async def test_should_not_detect(self):
        with open(
            abspath("./tests/fixtures/images/no_face.jpg"), "rb"
        ) as fixture:
            self.engine.load(fixture.read(), None)

        self.context.config.FACE_DETECTOR_CASCADE_FILE = abspath(
            "./thumbor/detectors/face_detector/haarcascade_frontalface_default.xml"
        )

        await FaceDetector(self.context, 0, []).detect()
        expect(self.context.request.focal_points).to_be_empty()

    @gen_test
    async def test_should_run_on_grayscale_images(self):
        with open(
            abspath(
                "./tests/fixtures/images/"
                "Giunchedi%2C_Filippo_January_2015_01-grayscale.jpg"
            ),
            "rb",
        ) as fixture:
            self.engine.load(fixture.read(), None)

        self.context.config.FACE_DETECTOR_CASCADE_FILE = abspath(
            "./thumbor/detectors/face_detector/haarcascade_frontalface_default.xml",
        )

        if hasattr(FaceDetector, "cascade"):
            del FaceDetector.cascade
        await FaceDetector(self.context, 0, None).detect()
        detection_result = self.context.request.focal_points[0]
        expect(detection_result.origin).to_equal("Face Detection")
        expect(detection_result.x).to_be_numeric()
        expect(detection_result.y).to_be_numeric()
        expect(detection_result.width).to_be_numeric()
        expect(detection_result.height).to_be_numeric()

    @gen_test
    async def test_should_run_on_cmyk_images(self):
        with open(
            abspath(
                "./tests/fixtures/images/"
                "Giunchedi%2C_Filippo_January_2015_01-cmyk.jpg"
            ),
            "rb",
        ) as fixture:
            self.engine.load(fixture.read(), None)

        self.context.config.FACE_DETECTOR_CASCADE_FILE = abspath(
            "./thumbor/detectors/face_detector/haarcascade_frontalface_default.xml",
        )

        if hasattr(FaceDetector, "cascade"):
            del FaceDetector.cascade
        await FaceDetector(self.context, 0, None).detect()
        detection_result = self.context.request.focal_points[0]
        expect(detection_result.origin).to_equal("Face Detection")
        expect(detection_result.x).to_be_numeric()
        expect(detection_result.y).to_be_numeric()
        expect(detection_result.width).to_be_numeric()
        expect(detection_result.height).to_be_numeric()

    @gen_test
    async def test_should_run_on_images_with_alpha(self):
        with open(
            abspath(
                "./tests/fixtures/images/Giunchedi%2C_Filippo_January_2015_01.png"
            ),
            "rb",
        ) as fixture:
            self.engine.load(fixture.read(), None)

        self.context.config.FACE_DETECTOR_CASCADE_FILE = abspath(
            "./thumbor/detectors/face_detector/haarcascade_frontalface_default.xml",
        )

        if hasattr(FaceDetector, "cascade"):
            del FaceDetector.cascade
        await FaceDetector(self.context, 0, None).detect()
        detection_result = self.context.request.focal_points[0]
        expect(detection_result.origin).to_equal("Face Detection")
        expect(detection_result.x).to_be_numeric()
        expect(detection_result.y).to_be_numeric()
        expect(detection_result.width).to_be_numeric()
        expect(detection_result.height).to_be_numeric()
