# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from tornado.testing import gen_test

from tests.base import FilterTestCase


class ProportionFilterTestCase(FilterTestCase):
    @gen_test
    async def test_proportion_filter_equal(self):
        image = await self.get_filtered(
            "source.jpg", "thumbor.filters.proportion", "proportion(0.60)"
        )
        expected = self.get_fixture("proportion.jpg")
        assert image.size == expected.size

    @gen_test
    async def test_proportion_filter_not_equal(self):
        image = await self.get_filtered(
            "source.jpg", "thumbor.filters.proportion", "proportion(0.90)"
        )
        expected = self.get_fixture("proportion.jpg")
        assert image.size != expected.size

    @gen_test
    async def test_proportion_filter_value_above_one_is_ignored(self):
        """Values > 1.0 must be rejected to prevent resource-exhaustion DoS."""
        original = await self.get_filtered(
            "source.jpg", "thumbor.filters.proportion", "proportion(1.0)"
        )
        oversized = await self.get_filtered(
            "source.jpg", "thumbor.filters.proportion", "proportion(10000)"
        )
        assert oversized.size == original.size

    @gen_test
    async def test_proportion_filter_zero_is_ignored(self):
        original = await self.get_filtered(
            "source.jpg", "thumbor.filters.proportion", "proportion(1.0)"
        )
        zeroed = await self.get_filtered(
            "source.jpg", "thumbor.filters.proportion", "proportion(0)"
        )
        assert zeroed.size == original.size

    @gen_test
    async def test_proportion_filter_negative_is_ignored(self):
        original = await self.get_filtered(
            "source.jpg", "thumbor.filters.proportion", "proportion(1.0)"
        )
        negative = await self.get_filtered(
            "source.jpg", "thumbor.filters.proportion", "proportion(-0.5)"
        )
        assert negative.size == original.size
