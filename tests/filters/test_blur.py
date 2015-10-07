#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from preggy import expect

from tests.base import FilterTestCase


class BlurFilterTestCase(FilterTestCase):
    def test_filter_processes_as_expected(self):
        image = self.get_filtered('blur_source.jpg', 'thumbor.filters.blur', 'blur(4,2)')
        expected = self.get_fixture('blur.jpg')

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)
