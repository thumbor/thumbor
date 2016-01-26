#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com
from unittest import skip

from preggy import expect

from tests.base import FilterTestCase


class ResponsiveTestCase(FilterTestCase):
    def test_no_op(self):
        # source size: 400x600

        image = self.get_filtered('source.jpg', 'thumbor.filters.responsive',
                                  'responsive()')
        expected = self.get_fixture('source.jpg')
        expect(len(image[0])).to_equal(400)
        expect(len(image)).to_equal(600)

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

        image = self.get_filtered('source.jpg', 'thumbor.filters.responsive',
                                  'responsive(1)')
        expected = self.get_fixture('source.jpg')

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

        image = self.get_filtered('source.jpg', 'thumbor.filters.responsive',
                                  'responsive(2)')
        expected = self.get_fixture('source.jpg')

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

    def test_no_op_with_fit_in(self):
        # fit_in = True
        def config_context(context):
            context.request.fit_in = True
            context.request.width = 400
            context.request.height = 600

        image = self.get_filtered('source.jpg', 'thumbor.filters.responsive',
                                  'responsive()', config_context=config_context)
        expect(len(image[0])).to_equal(400)
        expect(len(image)).to_equal(600)

        image = self.get_filtered('source.jpg', 'thumbor.filters.responsive',
                                  'responsive(1)', config_context=config_context)
        expect(len(image[0])).to_equal(400)
        expect(len(image)).to_equal(600)

        image = self.get_filtered('source.jpg', 'thumbor.filters.responsive',
                                  'responsive(2)', config_context=config_context)
        expect(len(image[0])).to_equal(400)
        expect(len(image)).to_equal(600)

        image = self.get_filtered('source.jpg', 'thumbor.filters.responsive',
                                  'responsive(0.5)', config_context=config_context)
        expect(len(image[0])).to_equal(400)
        expect(len(image)).to_equal(600)


    def test_smaller_dpr(self):
        image = self.get_filtered('source.jpg', 'thumbor.filters.responsive',
                                  'responsive(0.5)')

        expect(len(image[0])).to_equal(200)
        expect(len(image)).to_equal(300)

    def test_higher_dpr(self):
        def config_context(context):
            context.request.fit_in = False
            context.request.width = 200
            context.request.height = 300

        image = self.get_filtered(
                'source.jpg',
                'thumbor.filters.responsive',
                'responsive(2)',
                config_context=config_context)

        expect(len(image[0])).to_equal(400)
        expect(len(image)).to_equal(600)


        expected = self.get_fixture('source.jpg')
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

        def config_context(context):
            context.request.fit_in = False
            context.request.width = 100
            context.request.height = 150

        image = self.get_filtered(
                'source.jpg',
                'thumbor.filters.responsive',
                'responsive(2)',
                config_context=config_context)

        expect(len(image[0])).to_equal(200)
        expect(len(image)).to_equal(300)

    def test_higher_dpr_with_fit_in(self):
        # fit_in = True
        def config_context(context):
            context.request.fit_in = True
            context.request.width = 200
            context.request.height = 300

        image = self.get_filtered(
                'source.jpg',
                'thumbor.filters.responsive',
                'responsive(2)',
                config_context=config_context)

        expect(len(image[0])).to_equal(400)
        expect(len(image)).to_equal(600)

        expected = self.get_fixture('source.jpg')
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

        def config_context(context):
            context.request.fit_in = True
            context.request.width = 100
            context.request.height = 150

        image = self.get_filtered(
                'source.jpg',
                'thumbor.filters.responsive',
                'responsive(2)',
                config_context=config_context)

        expect(len(image[0])).to_equal(200)
        expect(len(image)).to_equal(300)
