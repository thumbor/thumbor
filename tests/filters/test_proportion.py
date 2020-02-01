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


class ProportionFilterTestCase(FilterTestCase):
    @gen_test
    async def test_proportion_filter_equal(self):
        image = await self.get_filtered(
            "source.jpg", "thumbor.filters.proportion", "proportion(0.60)"
        )
        expected = self.get_fixture("proportion.jpg")
        expect(image.size).to_equal(expected.size)

    @gen_test
    async def test_proportion_filter_not_equal(self):
        image = await self.get_filtered(
            "source.jpg", "thumbor.filters.proportion", "proportion(0.90)"
        )
        expected = self.get_fixture("proportion.jpg")
        expect(image.size).not_to_equal(expected.size)
