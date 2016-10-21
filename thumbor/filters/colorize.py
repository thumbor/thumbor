#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.filters import BaseFilter, filter_method
from thumbor.ext.filters import _colorize


class Filter(BaseFilter):

    @filter_method(BaseFilter.PositiveNumber, BaseFilter.PositiveNumber, BaseFilter.PositiveNumber, BaseFilter.String)
    def colorize(self, red_pct, green_pct, blue_pct, fill):
        fill_r, fill_g, fill_b = tuple(map(ord, fill.decode('hex')))
        mode, data = self.engine.image_data_as_rgb()
        imgdata = _colorize.apply(mode, red_pct, green_pct, blue_pct, fill_r, fill_g, fill_b, data)
        self.engine.set_image_data(imgdata)
