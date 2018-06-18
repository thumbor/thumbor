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


class BrightnessFilterTestCase(FilterTestCase):
    @tornado.testing.gen_test
    def test_brightness_filter(self):
        image = yield self.get_filtered('source.jpg', 'thumbor.filters.brightness', 'brightness(20)')
        expected = self.get_fixture('brightness.jpg')

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)
