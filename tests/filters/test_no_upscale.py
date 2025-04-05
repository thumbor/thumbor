#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2025 globo.com thumbor@googlegroups.com


from preggy import expect
from tornado.testing import gen_test

from tests.base import FilterTestCase


class FakeNoUpscaleEngine:
    @property
    def size(self):
        return (300, 200)

    def get_orientation(self):
        return 1


class NoUpscaleFilterTestCase(FilterTestCase):
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

        expect(self.context.request.width).to_equal(300)
        expect(self.context.request.height).to_equal(200)

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

        expect(self.context.request.width).to_equal(150)
        expect(self.context.request.height).to_equal(100)
