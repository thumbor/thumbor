#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.filters import BaseFilter, filter_method
from thumbor.ext.filters import _rgb


class Filter(BaseFilter):

    @filter_method(BaseFilter.Number, BaseFilter.Number, BaseFilter.Number)
    def rgb(self, r, g, b):
        mode, data = self.engine.image_data_as_rgb()
        imgdata = _rgb.apply(mode, r, g, b, data)
        self.engine.set_image_data(imgdata)
