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


class QualityFilterTestCase(FilterTestCase):
    @gen_test
    async def test_quality_filter(self):
        image = await self.get_filtered(
            "source.jpg", "thumbor.filters.quality", "quality(10)"
        )
        expected = self.get_fixture("quality-10%.jpg")

        expect(self.context.request.quality).to_equal(10)
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)
