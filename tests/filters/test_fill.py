#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com
import tornado
from preggy import expect

from tests.base import FilterTestCase


class FillFilterTestCase(FilterTestCase):
    @tornado.testing.gen_test
    def test_fill_filter_with_fixed_color(self):
        def config_context(context):
            context.request.fit_in = True
            context.request.width = 800
            context.request.height = 800

        image = yield self.get_filtered(
            'source.jpg',
            'thumbor.filters.fill',
            'fill(0000ff)',
            config_context=config_context
        )

        expected = self.get_fixture('fill.jpg')

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.97)

    @tornado.testing.gen_test
    def test_fill_filter_with_average(self):
        def config_context(context):
            context.request.fit_in = True
            context.request.width = 800
            context.request.height = 800

        image = yield self.get_filtered(
            'source.jpg',
            'thumbor.filters.fill',
            'fill(auto)',
            config_context=config_context
        )

        expected = self.get_fixture('fill2.jpg')

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.97)

    @tornado.testing.gen_test
    def test_fill_filter_with_full_fit_in(self):
        def config_context(context):
            context.request.fit_in = True
            context.request.full = True
            context.request.width = 800
            context.request.height = 800

        image = yield self.get_filtered(
            'source.jpg',
            'thumbor.filters.fill',
            'fill(auto)',
            config_context=config_context
        )

        expected = self.get_fixture('fill3.jpg')

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.97)

    @tornado.testing.gen_test
    def test_fill_filter_with_full_fit_in_orig_width(self):
        def config_context(context):
            context.request.fit_in = True
            context.request.full = True
            context.request.width = 'orig'
            context.request.height = 800

        image = yield self.get_filtered(
            'source.jpg',
            'thumbor.filters.fill',
            'fill(auto)',
            config_context=config_context
        )

        expected = self.get_fixture('fill3.jpg')

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.97)
