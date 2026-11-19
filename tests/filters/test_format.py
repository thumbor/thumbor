# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from os.path import abspath, dirname, join

from tornado.testing import gen_test

from tests.base import FilterTestCase

ANIMATED_GIF = abspath(
    join(dirname(__file__), "../fixtures/images/animated.gif")
)


class FormatFilterTestCase(FilterTestCase):
    @gen_test
    async def test_invalid_format_should_be_null(self):
        await self.get_filtered(
            "source.jpg", "thumbor.filters.format", "format(invalid)"
        )
        assert self.context.request.format is None

    @gen_test
    async def test_can_set_proper_format(self):
        await self.get_filtered(
            "source.jpg", "thumbor.filters.format", "format(webp)"
        )
        assert self.context.request.format == "webp"

    @gen_test
    async def test_can_set_jxl_format(self):
        await self.get_filtered(
            "source.jpg", "thumbor.filters.format", "format(jxl)"
        )
        assert self.context.request.format == "jxl"

    @gen_test
    async def test_multiple_frames_cannot_become_jxl(self):
        fltr = self.get_filter("thumbor.filters.format", "format(jxl)")
        with open(ANIMATED_GIF, "rb") as animated_gif:
            self.context.request.engine.load(animated_gif.read(), ".gif")

        await fltr.run()

        assert self.context.request.engine.is_multiple()
        assert self.context.request.format is None
