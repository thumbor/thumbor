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

from thumbor.detectors.face_detector import Detector as FaceDetector
from thumbor.engines.pil import Engine as PilEngine


class FaceDetectorTestCase(TestCase):
    def setUp(self):
        self.context = mock.Mock(request=mock.Mock(focal_points=[]))
        self.engine = PilEngine(self.context)
        self.context.modules.engine = self.engine

    def test_should_detect_one_face(self):
        with open(abspath('./tests/fixtures/images/one_face.jpg')) as f:
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
