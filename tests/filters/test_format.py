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


class FormatFilterTestCase(FilterTestCase):
    @gen_test
    async def test_invalid_format_should_be_null(self):
        await self.get_filtered(
            "source.jpg", "thumbor.filters.format", "format(invalid)"
        )
        expect(self.context.request.format).to_be_null()

    @gen_test
    async def test_can_set_proper_format(self):
        await self.get_filtered(
            "source.jpg", "thumbor.filters.format", "format(webp)"
        )
        expect(self.context.request.format).to_equal("webp")
