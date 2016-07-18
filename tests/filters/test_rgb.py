#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect

from tests.base import FilterTestCase


class RGBFilterTestCase(FilterTestCase):
    def test_rgb_filter(self):
        image = self.get_filtered('source.jpg', 'thumbor.filters.rgb', 'rgb(10,2,4)')
        expected = self.get_fixture('rgb.jpg')

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)
