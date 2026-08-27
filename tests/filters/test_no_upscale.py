# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2025 globo.com thumbor@googlegroups.com


from tornado.testing import gen_test

from tests.base import FilterTestCase


class FakeNoUpscaleEngine:
    @property
    def size(self):
        return (300, 200)

    def get_orientation(self):
        return 1


class FakeOrientedNoUpscaleEngine:
    @property
    def size(self):
        return (100, 200)

    def get_orientation(self):
        return 6


class NoUpscaleFilterTestCase(FilterTestCase):
    @gen_test
    async def test_original_dimensions_respect_orientation(self):
        fltr = self.get_filter(
            "thumbor.filters.no_upscale",
            "no_upscale()",
        )
        self.context.config.RESPECT_ORIENTATION = True
        self.context.request.width = "orig"
        self.context.request.height = "orig"
        self.context.request.engine = FakeOrientedNoUpscaleEngine()

        await fltr.run()

        assert self.context.request.width == 200
        assert self.context.request.height == 100

    @gen_test
    async def test_no_upscale_filter_with_original_dimensions(self):
        dimensions = (
            ("orig", "orig", 300, 200),
            ("orig", 100, 300, 100),
            (150, "orig", 150, 200),
        )

        for width, height, expected_width, expected_height in dimensions:
            fltr = self.get_filter(
                "thumbor.filters.no_upscale",
                "no_upscale()",
            )
            self.context.request.width = width
            self.context.request.height = height
            self.context.request.engine = FakeNoUpscaleEngine()

            await fltr.run()

            assert self.context.request.width == expected_width
            assert self.context.request.height == expected_height

    @gen_test
    async def test_no_upscale_filter_request_bigger_than_image(self):
        def config_context(context):
            context.request.width = 600
            context.request.height = 400
            context.request.engine = FakeNoUpscaleEngine()

        fltr = self.get_filter(
            "thumbor.filters.no_upscale",
            "no_upscale()",
            config_context=config_context,
        )

        await fltr.run()

        assert self.context.request.width == 300
        assert self.context.request.height == 200

    @gen_test
    async def test_no_upscale_filter_request_lower_than_image(self):
        def config_context(context):
            context.request.width = 150
            context.request.height = 100
            context.request.engine = FakeNoUpscaleEngine()

        fltr = self.get_filter(
            "thumbor.filters.no_upscale",
            "no_upscale()",
            config_context=config_context,
        )

        await fltr.run()

        assert self.context.request.width == 150
        assert self.context.request.height == 100
