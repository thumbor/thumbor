#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect
from tornado.testing import gen_test

from thumbor.filters.rotate import Filter as RotateFilter
from tests.integration.filters import FilterTestCase


class RotateFilterTestCase(FilterTestCase):

    def get_filter(self):
        return RotateFilter

    @gen_test
    def test_rotate_filter_0(self):
        filtered_image = yield self.get_filtered('rotate(0)', 'source.jpg')
        expected = self.get_fixture('source.jpg')

        expect(filtered_image).to_be_similar_to(expected)

    @gen_test
    def test_rotate_filter_90(self):
        filtered_image = yield self.get_filtered('rotate(90)', 'source.jpg')
        expected = self.get_fixture('rotate_90.jpg')

        expect(filtered_image).to_be_similar_to(expected)

    @gen_test
    def test_rotate_filter_180(self):
        filtered_image = yield self.get_filtered('rotate(180)', 'source.jpg')
        expected = self.get_fixture('rotate_180.jpg')

        expect(filtered_image).to_be_similar_to(expected)

    @gen_test
    def test_rotate_filter_270(self):
        filtered_image = yield self.get_filtered('rotate(270)', 'source.jpg')
        expected = self.get_fixture('rotate_270.jpg')

        expect(filtered_image).to_be_similar_to(expected)

    @gen_test
    def test_rotate_filter_360(self):
        filtered_image = yield self.get_filtered('rotate(360)', 'source.jpg')
        expected = self.get_fixture('source.jpg')

        expect(filtered_image).to_be_similar_to(expected)

    @gen_test
    def test_rotate_filter_with_invalid_value(self):
        filtered_image = yield self.get_filtered('rotate(181)', 'source.jpg')
        expected = self.get_fixture('source.jpg')

        expect(filtered_image).to_be_similar_to(expected)
