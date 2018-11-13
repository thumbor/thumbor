#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect
from tornado.testing import gen_test

from thumbor.filters.equalize import Filter as EqualizeFilter
from tests.integration.filters import FilterTestCase


class EqualizeFilterTestCase(FilterTestCase):

    def get_filter(self):
        return EqualizeFilter

    @gen_test
    def test_convolution_filter_normalized(self):
        filtered_image = yield self.get_filtered('equalize()', 'source.jpg')
        expected = self.get_fixture('equalize.jpg')

        expect(filtered_image).to_be_similar_to(expected)
