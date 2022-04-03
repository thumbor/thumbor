#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect
from tornado.testing import gen_test

from tests.base import FilterTestCase


class BlurFilterTestCase(FilterTestCase):
    @gen_test
    async def test_blur_filter_with_sigma(self):
        image = await self.get_filtered(
            "source.jpg", "thumbor.filters.blur", "blur(4,2)"
        )
        expected = self.get_fixture("blur.jpg")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

    @gen_test
    async def test_blur_filter_with_zero_radius(self):
        image = await self.get_filtered(
            "source.jpg", "thumbor.filters.blur", "blur(0)"
        )
        expected = self.get_fixture("source.jpg")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_equal(1)

    @gen_test
    async def test_blur_filter_without_sigma(self):
        image = await self.get_filtered(
            "source.jpg", "thumbor.filters.blur", "blur(8)"
        )
        expected = self.get_fixture("blur2.jpg")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

    @gen_test
    async def test_blur_filter_with_max_radius(self):
        image = await self.get_filtered(
            "source.jpg", "thumbor.filters.blur", "blur(500)"
        )
        expected = self.get_fixture("blur3.jpg")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

    @gen_test
    async def test_blur_filter_for_png_palette_mode(self):
        image = await self.get_filtered(
            "256_color_palette.png", "thumbor.filters.blur", "blur(10)"
        )
        expected = self.get_fixture("256_color_palette_blur_result.png")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

    @gen_test
    async def test_blur_filter_png_with_transparency_rgba_mode(self):
        image = await self.get_filtered(
            "PNG_transparency_demonstration_1.png",
            "thumbor.filters.blur",
            "blur(10)",
            mode="RGBA",
        )
        expected = self.get_fixture("blur4.png", mode="RGBA")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

    @gen_test
    async def test_blur_filter_png_with_transparency_la_mode(self):
        image = await self.get_filtered(
            "PNG_transparency_demonstration_1.png",
            "thumbor.filters.blur",
            "blur(10)",
            mode="LA",
        )
        expected = self.get_fixture("blur4.png", mode="LA")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)
