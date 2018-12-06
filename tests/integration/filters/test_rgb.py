#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect
from tornado.testing import gen_test

from thumbor.filters.rgb import Filter as RGBFilter
from tests.integration.filters import FilterTestCase


class RGBFilterTestCase(FilterTestCase):

    def get_filter(self):
        return RGBFilter

    @gen_test
    def test_rgb_filter(self):
        filtered_image = yield self.get_filtered('rgb(10,2,4)', 'source.jpg')
        expected = self.get_fixture('rgb.jpg')

        expect(filtered_image).to_be_similar_to(expected)
