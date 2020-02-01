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


class UpscaleFilterTestCase(FilterTestCase):
    @gen_test
    async def test_upscale_filter_with_fit_in_big(self):
        def config_context(context):
            context.request.fit_in = True
            context.request.width = 1000
            context.request.height = 1000

        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.upscale",
            "upscale()",
            config_context=config_context,
        )

        expected = self.get_fixture("upscale1.jpg")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.97)

    @gen_test
    async def test_upscale_filter_with_fit_in_small(self):
        def config_context(context):
            context.request.fit_in = True
            context.request.width = 400
            context.request.height = 400

        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.upscale",
            "upscale()",
            config_context=config_context,
        )

        expected = self.get_fixture("upscale2.jpg")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.97)

    @gen_test
    async def test_upscale_filter_with_full_fit_in(self):
        def config_context(context):
            context.request.fit_in = True
            context.request.full = True
            context.request.width = 800
            context.request.height = 800

        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.upscale",
            "upscale()",
            config_context=config_context,
        )

        expected = self.get_fixture("upscale3.jpg")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.97)

    @gen_test
    async def test_upscale_filter_with_adaptive_fit_in_big(self):
        def config_context(context):
            context.request.fit_in = True
            context.request.adaptive = True
            context.request.width = 1000
            context.request.height = 1200

        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.upscale",
            "upscale()",
            config_context=config_context,
        )

        expected = self.get_fixture("upscale4.jpg")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.97)

    @gen_test
    async def test_upscale_filter_with_adaptive_full_fit_in_big(self):
        def config_context(context):
            context.request.fit_in = True
            context.request.full = True
            context.request.adaptive = True
            context.request.width = 800
            context.request.height = 800

        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.upscale",
            "upscale()",
            config_context=config_context,
        )

        expected = self.get_fixture("upscale3.jpg")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.97)
