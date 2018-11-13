#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect
from tornado.testing import gen_test

from thumbor.filters.curve import Filter as CurveFilter
from tests.integration.filters import FilterTestCase


class CurveFilterTestCase(FilterTestCase):

    def get_filter(self):
        return CurveFilter

    @gen_test
    def test_convolution_filter_normalized(self):
        filtered_image = yield self.get_filtered('curve([(0,0),(40,59),(255,255)],[(32,59),(64,80),(92,111),(128,153),(140,169),(164,201),(192,214),(224,215),(240,214),(255,212)],[(34,41),(64,51),(92,76),(128,112),(140,124),(164,147),(192,180),(224,216),(240,236),(255,255)],[(40,46),(64,55),(92,83),(128,127),(140,144),(164,174),(192,197),(224,199),(240,197),(255,198)])', 'source.jpg')
        expected = self.get_fixture('curve.jpg')

        expect(filtered_image).to_be_similar_to(expected)
