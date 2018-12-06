#!/usr/bin/python
# -*- coding: utf-8 -*-
'''Filter Module'''

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from tornado import gen

from thumbor.filters import BaseFilter, filter_method
from thumbor.ext.filters import _noise
from thumbor import Engine


class Filter(BaseFilter):

    @gen.coroutine
    @filter_method(BaseFilter.PositiveNumber, BaseFilter.PositiveNumber)
    def noise(self, details, amount, seed=0):
        mode, data = yield Engine.get_image_data_as_rgb(self, details)
        imgdata = _noise.apply(mode, amount, data, seed)
        yield Engine.set_image_data(self, details, imgdata)
