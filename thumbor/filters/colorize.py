#!/usr/bin/python
# -*- coding: utf-8 -*-
'''Filter Module'''

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import codecs

from tornado import gen

from thumbor import Engine
from thumbor.filters import BaseFilter, filter_method
from thumbor.ext.filters import _colorize


class Filter(BaseFilter):
    '''Filter class'''

    @gen.coroutine
    @filter_method(BaseFilter.PositiveNumber, BaseFilter.PositiveNumber,
                   BaseFilter.PositiveNumber, BaseFilter.String)
    def colorize(self, details, red_pct, green_pct, blue_pct, fill):
        '''Changes the colors of the image's channels'''
        # fill_r, fill_g, fill_b = tuple(map(ord, fill_hex))
        fill_r, fill_g, fill_b = self.get_rgb(fill)
        mode, data = yield Engine.get_image_data_as_rgb(self, details)
        imgdata = _colorize.apply(mode, red_pct, green_pct, blue_pct, fill_r,
                                  fill_g, fill_b, data)
        yield Engine.set_image_data(self, details, imgdata)
