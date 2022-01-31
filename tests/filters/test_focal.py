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


class FocalFilterTestCase(FilterTestCase):
    @gen_test
    async def test_focal_filter_valid(self):
        await self.get_filtered(
            "source.jpg", "thumbor.filters.focal", "focal(146x156:279x208)"
        )

        expect(self.context.request.focal_points[0].origin).to_equal(
            "Explicit"
        )
        expect(self.context.request.focal_points[0].height).to_equal(52)
        expect(self.context.request.focal_points[0].width).to_equal(133)
        expect(self.context.request.focal_points[0].y).to_equal(182)
        expect(self.context.request.focal_points[0].x).to_equal(212)

    @gen_test
    async def test_focal_filter_no_change(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.focal",
            "focal(0x0:400x600)",
        )
        expected = self.get_fixture("source.jpg")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

    @gen_test
    async def test_focal_filter_pass_through_empty(self):
        image = await self.get_filtered(
            "source.jpg", "thumbor.filters.focal", "focal()"
        )
        expected = self.get_fixture("source.jpg")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

    @gen_test
    async def test_focal_filter_pass_through_invalid(self):
        image = await self.get_filtered(
            "source.jpg", "thumbor.filters.focal", "focal(0x0:0x0)"
        )
        expected = self.get_fixture("source.jpg")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

    @gen_test
    async def test_focal_filter_pass_through_dumb(self):
        image = await self.get_filtered(
            "source.jpg", "thumbor.filters.focal", "focal(lkasjdklfjlkajsfd)"
        )
        expected = self.get_fixture("source.jpg")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)
