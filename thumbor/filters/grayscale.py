#!/usr/bin/python
# -*- coding: utf-8 -*-
'''Filter Module'''

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
    @filter_method()
    def grayscale(self, details):
        yield Engine.convert_to_grayscale(self, details, update_image=True)
