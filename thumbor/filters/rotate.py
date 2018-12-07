#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from tornado import gen

from thumbor import Engine
from thumbor.filters import BaseFilter, filter_method


class Filter(BaseFilter):

    @gen.coroutine
    @filter_method(BaseFilter.Number)
    def rotate(self, details, value):
        if value % 90 == 0:
            value = value % 360  # To optimize for engines
            yield Engine.rotate(self, details, value)
