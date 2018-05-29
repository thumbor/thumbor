#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect
from tornado.testing import gen_test

from thumbor.filters.colorize import Filter as ColorizeFilter
from tests.integration.filters import FilterTestCase


class ColorizeFilterTestCase(FilterTestCase):

    def get_filter(self):
        return ColorizeFilter

    @gen_test
    def test_brightness_filter(self):
        filtered_image = yield self.get_filtered('colorize(40,80,20,ffffff)',
                                                 'source.jpg')
        expect(filtered_image).to_be_similar_to('colorize.jpg')
