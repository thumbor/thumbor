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


class RoundCornerFilterTestCase(FilterTestCase):
    @gen_test
    async def test_round_corner_filter_with_a_radius(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.round_corner",
            "round_corner(50,255,0,0)",
        )
        expected = self.get_fixture("round_corner.jpg")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

    @gen_test
    async def test_round_corner_filter_with_ab_radius(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.round_corner",
            "round_corner(50|75,255,0,0)",
        )
        expected = self.get_fixture("round_corner1.jpg")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

    @gen_test
    async def test_round_corner_filter_with_blue_background(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.round_corner",
            "round_corner(50,0,0,255)",
        )
        expected = self.get_fixture("round_corner2.jpg")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

    @gen_test
    async def test_round_corner_filter_without_transparent(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.round_corner",
            "round_corner(50,255,0,0,0)",
        )
        expected = self.get_fixture("round_corner3.jpg")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

    @gen_test
    async def test_round_corner_filter_with_transparent(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.round_corner",
            "round_corner(50,255,0,0,1)",
        )
        expected = self.get_fixture("round_corner3.jpg")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

    @gen_test
    async def test_round_corner_filter_with_transparent_by_png(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.round_corner",
            "round_corner(50,255,0,0,1)",
            mode="RGBA",
        )
        expected = self.get_fixture("round_corner.png", mode="RGBA")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

    @gen_test
    async def test_round_corner_filter_with_transparent_by_webp(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.round_corner",
            "round_corner(50,255,0,0,1)",
            mode="RGBA",
        )
        expected = self.get_fixture("round_corner.webp", mode="RGBA")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)
