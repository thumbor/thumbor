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


class BackgroundColorFilterTestCase(FilterTestCase):
    @tornado.testing.gen_test
    def test_background_color_filter_with_fixed_color(self):
        def config_context(context):
            context.request.fit_in = True
            context.request.width = 300
            context.request.height = 300

        image = yield self.get_filtered(
            'PNG_transparency_demonstration_1.png',
            'thumbor.filters.background_color',
            'background_color(blue)',
            config_context=config_context
        )

        expected = self.get_fixture('PNG_transparency_demonstration_1_blue.png')

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.97)
