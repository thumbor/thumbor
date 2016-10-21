#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect

from tests.base import FilterTestCase


class ColorizeFilterTestCase(FilterTestCase):
    def test_colorize_filter(self):
        image = self.get_filtered('source.jpg', 'thumbor.filters.colorize', 'colorize(40,80,20,ffffff)')
        expected = self.get_fixture('colorize.jpg')

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.97)
