#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect

from tests.base import FilterTestCase


class StretchFilterTestCase(FilterTestCase):
    def test_stretch_filter(self):
        self.get_filtered('source.jpg', 'thumbor.filters.stretch', 'stretch()')
        expect(self.context.request.stretch).to_be_true()
