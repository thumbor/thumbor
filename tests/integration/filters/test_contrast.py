#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect
from tornado.testing import gen_test

from thumbor.filters.contrast import Filter as ContrastFilter
from tests.integration.filters import FilterTestCase


class ContrastFilterTestCase(FilterTestCase):

    def get_filter(self):
        return ContrastFilter

    @gen_test
    def test_contrast_filter(self):
        filtered_image = yield self.get_filtered('contrast(20)',
                                                 'source.jpg')
        expected = self.get_fixture('contrast.jpg')
        expect(filtered_image).to_be_similar_to(expected)

    @gen_test
    def test_contrast_negative_filter(self):
        filtered_image = yield self.get_filtered('contrast(-20)',
                                                 'source.jpg')
        expected = self.get_fixture('negative_contrast.jpg')
        expect(filtered_image).to_be_similar_to(expected)
