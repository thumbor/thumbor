#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect
from tornado.testing import gen_test

from thumbor.filters.convolution import Filter as ConvolutionFilter
from tests.integration.filters import FilterTestCase


class ConvolutionFilterTestCase(FilterTestCase):

    def get_filter(self):
        return ConvolutionFilter

    @gen_test
    def test_convolution_filter_normalized(self):
        filtered_image = yield self.get_filtered('convolution(1;2;1;2;4;2;1;2;1,3,true)', 'source.jpg')
        expected = self.get_fixture('convolution_normalized.jpg')

        expect(filtered_image).to_be_similar_to(expected)

    @gen_test
    def test_convolution_filter_unnormalized(self):
        filtered_image = yield self.get_filtered('convolution(-1;-1;-1;-1;8;-1;-1;-1;-1,3,false)', 'source.jpg')
        expected = self.get_fixture('convolution_unnormalized.jpg')

        expect(filtered_image).to_be_similar_to(expected)
