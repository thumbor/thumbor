#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from tornado import gen

from thumbor.filters import BaseFilter, filter_method


class Filter(BaseFilter):

    @gen.coroutine
    @filter_method(BaseFilter.PositiveNumber)
    def max_age(self, details, value):
        details.headers['Cache-Control'] = f'max-age={value}'
