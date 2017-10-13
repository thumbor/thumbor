#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com
import tornado
from preggy import expect
from tests.base import FilterTestCase
from thumbor.point import FocalPoint


class RedEyeFilterTestCase(FilterTestCase):
    @tornado.testing.gen_test
    def test_redeye_passthrough_when_no_face_points(self):
        image = yield self.get_filtered(
            'redeye.png',
            'thumbor.filters.redeye',
            'red_eye()'
        )

        expected = self.get_fixture('redeye.png')

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

    @tornado.testing.gen_test
    def test_redeye_applied(self):
        expected = self.get_fixture('redeye_applied.png')

        def config_context(context):
            image_w, image_h = expected.size[0], expected.size[1]
            point = FocalPoint.from_square(50, 50, image_w - 100, image_h - 100, origin='Face Detection')

            context.request.focal_points = [point]

        image = yield self.get_filtered(
            'redeye.png',
            'thumbor.filters.redeye',
            'red_eye()',
            config_context
        )

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)
