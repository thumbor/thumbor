#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect
from tornado.testing import gen_test

from thumbor.filters.round_corner import Filter as RoundCorner
from tests.integration.filters import FilterTestCase


class RoundCornerFilterTestCase(FilterTestCase):

    def get_filter(self):
        return RoundCorner

    @gen_test
    def test_round_corner(self):
        filtered_image = yield self.get_filtered('round_corner(20|40,0,0,0)', 'source.jpg')
        expected = self.get_fixture('round_corner1.jpg')
        expect(filtered_image).to_be_similar_to(expected)
    
    @gen_test
    def test_round_corner2(self):
        filtered_image = yield self.get_filtered('round_corner(200|200,0,0,0)', 'source.jpg')
        expected = self.get_fixture('round_corner2.jpg')
        expect(filtered_image).to_be_similar_to(expected)

