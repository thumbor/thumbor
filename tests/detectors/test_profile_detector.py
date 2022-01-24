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

from tests.base import DetectorTestCase
from thumbor.detectors.profile_detector import Detector


class ProfileDetectorTestCase(DetectorTestCase):
    @gen_test
    async def test_detector_uses_proper_cascade(self):
        cascade = "./tests/fixtures/haarcascade_profileface.xml"
        ctx = mock.Mock(
            config=mock.Mock(
                PROFILE_DETECTOR_CASCADE_FILE=abspath(cascade),
            )
        )

        detector = Detector(ctx, 1, [])
        expect(detector).not_to_be_null()
