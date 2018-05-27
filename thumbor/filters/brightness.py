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
from thumbor.ext.filters import _brightness
from thumbor import Engine


class Filter(BaseFilter):
    '''Filter class'''

    @gen.coroutine
    @filter_method(BaseFilter.Number)
    def brightness(self, details, value):
        '''Changes the overall brightness of the image'''
        mode, data = yield Engine.get_image_data_as_rgb(self, details)
        imgdata = _brightness.apply(mode, value, data)
        yield Engine.set_image_data(self, details, imgdata)
