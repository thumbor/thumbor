#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect
from tornado.testing import gen_test

from thumbor.filters.sharpen import Filter as SharpenFilter
from tests.integration.filters import FilterTestCase


class SharpenFilterTestCase(FilterTestCase):

    def get_filter(self):
        return SharpenFilter

    @gen_test
    def test_sharpen_filter_sharpen_amount(self):
        filtered_image = yield self.get_filtered('sharpen(9,1.0,true)', 'source.jpg')

        expected = self.get_fixture('sharpen.jpg')
        expect(filtered_image).to_be_similar_to(expected)
