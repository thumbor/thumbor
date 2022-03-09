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


class SaturationFilterTestCase(FilterTestCase):
    @gen_test
    async def test_saturation_filter(self):
        image = await self.get_filtered(
            "source.jpg", "thumbor.filters.saturation", "saturation(10)"
        )
        expected = self.get_fixture("saturation.png")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)
