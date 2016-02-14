#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com


from preggy import expect

from tests.base import FilterTestCase


class FocalFilterTestCase(FilterTestCase):
    def test_focal_filter_fit_in(self):
        def config_context(context):
            context.request.fit_in = True
            context.request.width = 400
            context.request.height = 100

        image = self.get_filtered(
            'source.jpg',
            'thumbor.filters.focal',
            'focal(146x156:279x208)',
            config_context=config_context
        )
        expected = self.get_fixture('focal.jpg')

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

    def test_focal_filter_pass_through_empty(self):
        image = self.get_filtered(
            'source.jpg',
            'thumbor.filters.focal',
            'focal()'
        )
        expected = self.get_fixture('source.jpg')

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

    def test_focal_filter_pass_through_invalid(self):
        image = self.get_filtered(
            'source.jpg',
            'thumbor.filters.focal',
            'focal(0x0:0x0)'
        )
        expected = self.get_fixture('source.jpg')

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

    def test_focal_filter_pass_through_dumb(self):
        image = self.get_filtered(
            'source.jpg',
            'thumbor.filters.focal',
            'focal(lkasjdklfjlkajsfd)'
        )
        expected = self.get_fixture('source.jpg')

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)
