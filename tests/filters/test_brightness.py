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


class BrightnessFilterTestCase(FilterTestCase):
    @gen_test
    async def test_brightness_filter(self):
        image = await self.get_filtered(
            "source.jpg", "thumbor.filters.brightness", "brightness(20)"
        )
        expected = self.get_fixture("brightness.jpg")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)
