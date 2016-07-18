#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from os.path import abspath

from preggy import expect

from thumbor.detectors.face_detector import Detector as FaceDetector
from tests.base import DetectorTestCase


class FaceDetectorTestCase(DetectorTestCase):
    def test_should_detect_one_face(self):
        with open(abspath('./tests/fixtures/images/Giunchedi%2C_Filippo_January_2015_01.jpg')) as f:
            self.engine.load(f.read(), None)

        for i, detector in enumerate([
            './thumbor/detectors/face_detector/haarcascade_frontalface_default.xml',
            './thumbor/detectors/face_detector/haarcascade_frontalface_alt.xml',
            './thumbor/detectors/face_detector/haarcascade_frontalface_alt2.xml',
            './thumbor/detectors/face_detector/haarcascade_frontalface_alt_tree.xml'
        ]):
            self.context.config.FACE_DETECTOR_CASCADE_FILE = abspath(
                detector
            )
            if hasattr(FaceDetector, 'cascade'):
                del FaceDetector.cascade
            FaceDetector(self.context, 0, None).detect(lambda: None)
            detection_result = self.context.request.focal_points[i]
            expect(detection_result.origin).to_equal('Face Detection')
            expect(detection_result.x).to_be_numeric()
            expect(detection_result.y).to_be_numeric()
            expect(detection_result.width).to_be_numeric()
            expect(detection_result.height).to_be_numeric()

    def test_should_not_detect(self):
        with open(abspath('./tests/fixtures/images/no_face.jpg')) as f:
            self.engine.load(f.read(), None)

        self.context.config.FACE_DETECTOR_CASCADE_FILE = abspath(
            './thumbor/detectors/face_detector/haarcascade_frontalface_default.xml'
        )

        FaceDetector(self.context, 0, []).detect(lambda: None)
        expect(self.context.request.focal_points).to_be_empty()

    def test_should_run_on_grayscale_images(self):
        with open(abspath('./tests/fixtures/images/Giunchedi%2C_Filippo_January_2015_01-grayscale.jpg')) as f:
            self.engine.load(f.read(), None)

        self.context.config.FACE_DETECTOR_CASCADE_FILE = abspath(
            './thumbor/detectors/face_detector/haarcascade_frontalface_default.xml',
        )
        if hasattr(FaceDetector, 'cascade'):
            del FaceDetector.cascade
        FaceDetector(self.context, 0, None).detect(lambda: None)
        detection_result = self.context.request.focal_points[0]
        expect(detection_result.origin).to_equal('Face Detection')
        expect(detection_result.x).to_be_numeric()
        expect(detection_result.y).to_be_numeric()
        expect(detection_result.width).to_be_numeric()
        expect(detection_result.height).to_be_numeric()

    def test_should_run_on_cmyk_images(self):
        with open(abspath('./tests/fixtures/images/Giunchedi%2C_Filippo_January_2015_01-cmyk.jpg')) as f:
            self.engine.load(f.read(), None)

        self.context.config.FACE_DETECTOR_CASCADE_FILE = abspath(
            './thumbor/detectors/face_detector/haarcascade_frontalface_default.xml',
        )
        if hasattr(FaceDetector, 'cascade'):
            del FaceDetector.cascade
        FaceDetector(self.context, 0, None).detect(lambda: None)
        detection_result = self.context.request.focal_points[0]
        expect(detection_result.origin).to_equal('Face Detection')
        expect(detection_result.x).to_be_numeric()
        expect(detection_result.y).to_be_numeric()
        expect(detection_result.width).to_be_numeric()
        expect(detection_result.height).to_be_numeric()

    def test_should_run_on_images_with_alpha(self):
        with open(abspath('./tests/fixtures/images/Giunchedi%2C_Filippo_January_2015_01.png')) as f:
            self.engine.load(f.read(), None)

        self.context.config.FACE_DETECTOR_CASCADE_FILE = abspath(
            './thumbor/detectors/face_detector/haarcascade_frontalface_default.xml',
        )
        if hasattr(FaceDetector, 'cascade'):
            del FaceDetector.cascade
        FaceDetector(self.context, 0, None).detect(lambda: None)
        detection_result = self.context.request.focal_points[0]
        expect(detection_result.origin).to_equal('Face Detection')
        expect(detection_result.x).to_be_numeric()
        expect(detection_result.y).to_be_numeric()
        expect(detection_result.width).to_be_numeric()
        expect(detection_result.height).to_be_numeric()
