# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from tornado.testing import gen_test

from tests.base import FilterTestCase


class StretchFilterTestCase(FilterTestCase):
    @gen_test
    async def test_stretch_filter(self):
        await self.get_filtered(
            "source.jpg", "thumbor.filters.stretch", "stretch()"
        )
        assert self.context.request.stretch is True

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
        assert ssim > 0.98
