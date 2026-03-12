# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from tornado.testing import gen_test

from tests.base import FilterTestCase


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
