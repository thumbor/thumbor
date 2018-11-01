#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect

from tests.base import FilterTestCase


class BlurFilterTestCase(FilterTestCase):
    def test_blur_filter_with_sigma(self):
        image = self.get_filtered('source.jpg', 'thumbor.filters.blur', 'blur(4,2)')
        expected = self.get_fixture('blur.jpg')

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

    def test_blur_filter_with_zero_radius(self):
        image = self.get_filtered('source.jpg', 'thumbor.filters.blur', 'blur(0)')
        expected = self.get_fixture('source.jpg')

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_equal(1)

    def test_blur_filter_without_sigma(self):
        image = self.get_filtered('source.jpg', 'thumbor.filters.blur', 'blur(8)')
        expected = self.get_fixture('blur2.jpg')

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

    def test_blur_filter_with_max_radius(self):
        image = self.get_filtered('source.jpg', 'thumbor.filters.blur', 'blur(500)')
        expected = self.get_fixture('blur3.jpg')

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

    def test_blur_filter_for_png_palette_mode(self):
        image = self.get_filtered('256_color_palette.png', 'thumbor.filters.blur', 'blur(10)')
        expected = self.get_fixture('256_color_palette_blur_result.png')

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)
