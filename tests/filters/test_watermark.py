#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect

from tests.base import FilterTestCase


class WatermarkFilterTestCase(FilterTestCase):
    def test_watermark_filter_centered(self):
        image = self.get_filtered('source.jpg', 'thumbor.filters.watermark', 'watermark(watermark.png,center,center,60)')
        expected = self.get_fixture('watermarkCenter.jpg')
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)

    def test_watermark_filter_centered_x(self):
        image = self.get_filtered('source.jpg', 'thumbor.filters.watermark', 'watermark(watermark.png,center,40,20)')
        expected = self.get_fixture('watermarkCenterX.jpg')
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)

    def test_watermark_filter_centered_y(self):
        image = self.get_filtered('source.jpg', 'thumbor.filters.watermark', 'watermark(watermark.png,80,center,50)')
        expected = self.get_fixture('watermarkCenterY.jpg')
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)

    def test_watermark_filter_repeated(self):
        image = self.get_filtered('source.jpg', 'thumbor.filters.watermark', 'watermark(watermark.png,repeat,repeat,70)')
        expected = self.get_fixture('watermarkRepeat.jpg')
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)

    def test_watermark_filter_repeated_x(self):
        image = self.get_filtered('source.jpg', 'thumbor.filters.watermark', 'watermark(watermark.png,repeat,center,70)')
        expected = self.get_fixture('watermarkRepeatX.jpg')
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)

    def test_watermark_filter_repeated_y(self):
        image = self.get_filtered('source.jpg', 'thumbor.filters.watermark', 'watermark(watermark.png,30,repeat,30)')
        expected = self.get_fixture('watermarkRepeatY.jpg')
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)

    def test_watermark_filter_simple(self):
        image = self.get_filtered('source.jpg', 'thumbor.filters.watermark', 'watermark(watermark.png,30,-50,60)')
        expected = self.get_fixture('watermarkSimple.jpg')
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)
