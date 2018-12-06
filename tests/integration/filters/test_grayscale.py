#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect
from tornado.testing import gen_test

from thumbor.filters.grayscale import Filter as GrayscaleFilter
from tests.integration.filters import FilterTestCase


class GrayscaleFilterTestCase(FilterTestCase):

    def get_filter(self):
        return GrayscaleFilter

    @gen_test
    def test_blur_filter_with_sigma(self):
        filtered_image = yield self.get_filtered('grayscale()', 'source.jpg')
        expected = self.get_fixture('grayscale.jpg')

        expect(filtered_image).to_be_similar_to(expected)
