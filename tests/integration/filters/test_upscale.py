#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect
from tornado.testing import gen_test

from thumbor.filters.upscale import Filter as UpscaleFilter
from tests.integration.filters import FilterTestCase


class UpscaleFilterTestCase(FilterTestCase):

    def get_filter(self):
        return UpscaleFilter


    @gen_test
    def test_upscale_filter_with_fit_in_big(self):
        filtered_image = yield self.get_filtered(pre_path='/unsafe/fit-in/1000x1000/', filter_str='upscale()', source_image='source.jpg')
        
        expected = self.get_fixture('upscale1.jpg')
        expect(filtered_image).to_be_similar_to(expected)

    @gen_test
    def test_upscale_filter_with_fit_in_small(self):
        filtered_image = yield self.get_filtered(pre_path='/unsafe/fit-in/400x400/', filter_str='upscale()', source_image='source.jpg')
        
        expected = self.get_fixture('upscale2.jpg')
        expect(filtered_image).to_be_similar_to(expected)

    @gen_test
    def test_upscale_filter_with_full_fit_in(self):
        filtered_image = yield self.get_filtered(pre_path='/unsafe/full-fit-in/800x800/', filter_str='upscale()', source_image='source.jpg')
        
        expected = self.get_fixture('upscale3.jpg')
        expect(filtered_image).to_be_similar_to(expected)

    @gen_test
    def test_upscale_filter_with_adaptive_fit_in_big(self):
        filtered_image = yield self.get_filtered(pre_path='/unsafe/adaptive-fit-in/1000x1200/', filter_str='upscale()', source_image='source.jpg')
        
        expected = self.get_fixture('upscale4.jpg')
        expect(filtered_image).to_be_similar_to(expected)

    @gen_test
    def test_upscale_filter_with_adaptive_full_fit_in_big(self):
        filtered_image = yield self.get_filtered(pre_path='/unsafe/adaptive-full-fit-in/800x800/', filter_str='upscale()', source_image='source.jpg')
        
        expected = self.get_fixture('upscale3.jpg')
        expect(filtered_image).to_be_similar_to(expected)
