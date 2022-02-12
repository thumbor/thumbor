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


class FillFilterTestCase(FilterTestCase):
    @gen_test
    async def test_fill_filter_with_fixed_color(self):
        def config_context(context):
            context.request.fit_in = True
            context.request.width = 800
            context.request.height = 800

        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.fill",
            "fill(0000ff)",
            config_context=config_context,
        )

        expected = self.get_fixture("fill.jpg")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.97)

    @gen_test
    async def test_fill_filter_with_average(self):
        def config_context(context):
            context.request.fit_in = True
            context.request.width = 800
            context.request.height = 800

        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.fill",
            "fill(auto)",
            config_context=config_context,
        )

        expected = self.get_fixture("fill2.jpg")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.97)

    @gen_test
    async def test_fill_filter_with_full_fit_in(self):
        def config_context(context):
            context.request.fit_in = True
            context.request.full = True
            context.request.width = 800
            context.request.height = 800

        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.fill",
            "fill(auto)",
            config_context=config_context,
        )

        expected = self.get_fixture("fill3.jpg")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.97)

    @gen_test
    async def test_fill_filter_with_full_fit_in_orig_width(self):
        def config_context(context):
            context.request.fit_in = True
            context.request.full = True
            context.request.width = "orig"
            context.request.height = 800

        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.fill",
            "fill(auto)",
            config_context=config_context,
        )

        expected = self.get_fixture("fill3.jpg")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.97)

    @gen_test
    async def test_fill_filter_with_blur(self):
        def config_context(context):
            context.request.fit_in = True
            context.request.width = 800
            context.request.height = 800

        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.fill",
            "fill(blur)",
            config_context=config_context,
        )

        expected = self.get_fixture("fill4.jpg")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.97)

    @gen_test
    async def test_fill_filter_with_blur_transparency_true(self):
        def config_context(context):
            context.request.fit_in = True
            context.request.width = 300
            context.request.height = 325

        image = await self.get_filtered(
            "PNG_transparency_demonstration_1.png",
            "thumbor.filters.fill",
            "fill(blur,true)",
            config_context=config_context,
            mode="RGBA",
        )

        expected = self.get_fixture("fill5.png", mode="RGBA")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)
