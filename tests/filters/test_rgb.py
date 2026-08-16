# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from tornado.testing import gen_test

from tests.base import FilterTestCase
from thumbor.ext.filters import _rgb


class RGBFilterTestCase(FilterTestCase):
    @gen_test
    async def test_rgb_filter(self):
        image = await self.get_filtered(
            "source.jpg", "thumbor.filters.rgb", "rgb(10,2,4)"
        )
        expected = self.get_fixture("rgb.jpg")

        ssim = self.get_ssim(image, expected)
        assert ssim > 0.98


def test_rgb_saturates_out_of_range_deltas():
    result = _rgb.apply("RGB", 10**8, -(10**8), 0, bytes([10, 128, 200]))

    assert result == bytes([255, 0, 200])
