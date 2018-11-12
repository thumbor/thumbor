#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect
from tornado.testing import gen_test

from thumbor.filters.blur import Filter as BlurFilter
from tests.integration.filters import FilterTestCase


class BlurFilterTestCase(FilterTestCase):

    def get_filter(self):
        return BlurFilter

    @gen_test
    def test_blur_filter_with_sigma(self):
        filtered_image = yield self.get_filtered('blur(4,2)', 'source.jpg')
        expected = self.get_fixture('blur.jpg')

        expect(filtered_image).to_be_similar_to(expected)

    @gen_test
    def test_blur_filter_without_sigma(self):
        filtered_image = yield self.get_filtered('blur(8)', 'source.jpg')
        expected = self.get_fixture('blur2.jpg')

        expect(filtered_image).to_be_similar_to(expected)

    @gen_test
    def test_blur_filter_with_max_radius(self):
        filtered_image = yield self.get_filtered('blur(500)', 'source.jpg')
        expected = self.get_fixture('blur3.jpg')

        expect(filtered_image).to_be_similar_to(expected)
