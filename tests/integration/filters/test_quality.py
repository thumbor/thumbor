#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect
from tornado.testing import gen_test

from thumbor.filters.quality import Filter as QualityFilter
from tests.integration.filters import FilterTestCase


class QualityFilterTestCase(FilterTestCase):

    def get_filter(self):
        return QualityFilter

    @gen_test
    def test_quality_filter(self):
        filtered_image = yield self.get_filtered('quality(10)', 'source.jpg')
        expected = self.get_fixture('quality-10%.jpg')

        expect(filtered_image).to_be_similar_to(expected)
