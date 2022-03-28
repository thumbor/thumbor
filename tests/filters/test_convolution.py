#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2022 globo.com thumbor@googlegroups.com

from preggy import expect
from tornado.testing import gen_test

from tests.base import FilterTestCase


class ConvolutionFilterTestCase(FilterTestCase):
    @gen_test
    async def test_convolution_filter_true(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.convolution",
            "convolution(1;2;1;2;4;2;1;2;1,3,true)",
        )
        expected = self.get_fixture("convolution-true.png")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

    @gen_test
    async def test_convolution_filter_false(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.convolution",
            "convolution(-1;-1;-1;-1;8;-1;-1;-1;-1,3,false)",
        )
        expected = self.get_fixture("convolution-false.png")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)
