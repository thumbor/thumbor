#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from preggy import expect

from tests.base import FilterTestCase


class RotateFilterTestCase(FilterTestCase):
    def test_rotate_filter(self):
        image = self.get_filtered('source.jpg', 'thumbor.filters.rotate', 'rotate(180)')
        expected = self.get_fixture('rotate.jpg')

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_equal(1)

    def test_rotate_filter_with_invalid_value(self):
        image = self.get_filtered('source.jpg', 'thumbor.filters.rotate', 'rotate(181)')
        expected = self.get_fixture('source.jpg')

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_equal(1)
