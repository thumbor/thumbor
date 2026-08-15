# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from tornado.testing import gen_test

from tests.base import FilterTestCase


class ContrastFilterTestCase(FilterTestCase):
    @gen_test
    async def test_contrast_filter(self):
        image = await self.get_filtered(
            "source.jpg", "thumbor.filters.contrast", "contrast(20)"
        )
        expected = self.get_fixture("contrast.jpg")

        ssim = self.get_ssim(image, expected)
        assert ssim > 0.98
