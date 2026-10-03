# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from tornado.testing import gen_test

from tests.base import FilterTestCase
from thumbor.ext.filters import _colorize


class ColorizeFilterTestCase(FilterTestCase):
    @gen_test
    async def test_colorize_filter(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.colorize",
            "colorize(40,80,20,ffffff)",
        )
        expected = self.get_fixture("colorize.jpg")

        ssim = self.get_ssim(image, expected)
        assert ssim > 0.97


def test_colorize_truncates_the_weighted_average():
    result = _colorize.apply("RGB", 50, 50, 50, 0, 0, 0, bytes([201, 3, 255]))

    assert result == bytes([100, 1, 127])


def test_colorize_saturates_out_of_range_percentages():
    result = _colorize.apply(
        "RGB", 10**8, 10**8, 10**8, 255, 0, 0, bytes([10, 10, 10])
    )

    assert result == bytes([255, 0, 0])
