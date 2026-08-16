# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from tornado.testing import gen_test

from tests.base import FilterTestCase
from thumbor.ext.filters import _brightness


class BrightnessFilterTestCase(FilterTestCase):
    @gen_test
    async def test_brightness_filter(self):
        image = await self.get_filtered(
            "source.jpg", "thumbor.filters.brightness", "brightness(20)"
        )
        expected = self.get_fixture("brightness.jpg")

        ssim = self.get_ssim(image, expected)
        assert ssim > 0.99


def test_brightness_saturates_out_of_range_deltas():
    pixel = bytes([0, 128, 255])

    assert _brightness.apply("RGB", 10**8, pixel) == bytes([255, 255, 255])
    assert _brightness.apply("RGB", -(10**8), pixel) == bytes([0, 0, 0])
