# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from tornado.testing import gen_test

from tests.base import FilterTestCase


def fit_in(width, height):
    def config_context(context):
        context.request.fit_in = True
        context.request.width = width
        context.request.height = height

    return config_context


class UpscaleFilterTestCase(FilterTestCase):
    async def get_upscaled(self, width, height):
        return await self.get_filtered(
            "source.jpg",
            "thumbor.filters.upscale",
            "upscale()",
            config_context=fit_in(width, height),
        )

    @gen_test
    async def test_upscale_filter_with_an_omitted_dimension(self):
        source_width, source_height = self.get_fixture("source.jpg").size

        for width, height in ((1000, 0), (805, 0), (0, 1000)):
            image = await self.get_upscaled(width, height)

            if width:
                expected = (width, int(source_height * width / source_width))
            else:
                expected = (int(source_width * height / source_height), height)
            assert image.size == expected, (width, height)

    @gen_test
    async def test_upscale_filter_with_orig_keeps_the_source_size(self):
        source_size = self.get_fixture("source.jpg").size

        for width, height in (
            ("orig", "orig"),
            ("orig", 1000),
            (1000, "orig"),
        ):
            image = await self.get_upscaled(width, height)

            assert image.size == source_size, (width, height)

    @gen_test
    async def test_upscale_filter_without_a_size_keeps_the_source_size(self):
        image = await self.get_upscaled(0, 0)

        assert image.size == self.get_fixture("source.jpg").size

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
        assert ssim > 0.97

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
        assert ssim > 0.97

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
        assert ssim > 0.97

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
        assert ssim > 0.97

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
        assert ssim > 0.97
