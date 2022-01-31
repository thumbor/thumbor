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


class StretchFilterTestCase(FilterTestCase):
    @gen_test
    async def test_stretch_filter(self):
        await self.get_filtered(
            "source.jpg", "thumbor.filters.stretch", "stretch()"
        )
        expect(self.context.request.stretch).to_be_true()

    @gen_test
    async def test_stretch_filter_with_resize(self):
        def config_context(context):
            context.request.width = 300
            context.request.height = 533
            context.request.stretch = True

        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.stretch",
            "stretch()",
            config_context=config_context,
        )

        expected = self.get_fixture("stretch.jpg")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)
