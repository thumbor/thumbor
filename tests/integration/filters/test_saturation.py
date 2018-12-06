#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect
from tornado.testing import gen_test

from thumbor.filters.saturation import Filter as SaturationFilter
from tests.integration.filters import FilterTestCase


class SaturationFilterTestCase(FilterTestCase):

    def get_filter(self):
        return SaturationFilter

    @gen_test
    def test_saturation_0_filter(self):
        filtered_image = yield self.get_filtered('saturation(0.0)', 'source.jpg')
        expected = self.get_fixture('saturation0.jpg')

        expect(filtered_image).to_be_similar_to(expected)

    @gen_test
    def test_saturation_1_filter(self):
        filtered_image = yield self.get_filtered('saturation(1.0)', 'source.jpg')
        expected = self.get_fixture('source.jpg')

        expect(filtered_image).to_be_similar_to(expected)

    @gen_test
    def test_saturation_2_filter(self):
        filtered_image = yield self.get_filtered('saturation(2.0)', 'source.jpg')
        expected = self.get_fixture('saturation2.jpg')

        expect(filtered_image).to_be_similar_to(expected)

