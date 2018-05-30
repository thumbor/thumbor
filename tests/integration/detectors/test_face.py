#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect
from tornado.testing import gen_test

import thumbor.blueprints.detectors.face as face_detector
from tests.integration.detectors import DetectorTestCase


class FaceDetectorTestCase(DetectorTestCase):

    def get_detector_blueprint(self):
        return face_detector

    @gen_test
    def test_face_detector(self):
        cropped_image = yield self.smart_detect(
            'face.jpg', width=100, height=300)
        expect(cropped_image).to_be_similar_to(
            self.get_fixture('face-detect-100x300.jpg'))
