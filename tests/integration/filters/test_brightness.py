#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect
from tornado.testing import gen_test

from thumbor.filters.brightness import Filter as BrightnessFilter
from tests.integration.filters import FilterTestCase


class BrightnessFilterTestCase(FilterTestCase):

    def get_filter(self):
        return BrightnessFilter

    @gen_test
    def test_brightness_filter(self):
        filtered_image = yield self.get_filtered('brightness(20)', 'source.jpg')
        expect(filtered_image).to_be_similar_to(
            self.get_fixture('brightness.jpg'))
