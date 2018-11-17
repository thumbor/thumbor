#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect
from tornado.testing import gen_test

from thumbor.filters.noise import Filter as NoiseFilter
from tests.integration.filters import FilterTestCase


class NoiseFilterTestCase(FilterTestCase):

    def get_filter(self):
        return NoiseFilter

    @gen_test
    def test_noise_filter(self):
        filtered_image = yield self.get_filtered('noise(200,123)', 'source.jpg')
        expected = self.get_fixture('noise.jpg')

        expect(filtered_image).to_be_similar_to(expected)
