#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.filters import BaseFilter, filter_method
from thumbor.ext.filters import _sharpen


class Filter(BaseFilter):

    @filter_method(BaseFilter.DecimalNumber, BaseFilter.DecimalNumber, BaseFilter.Boolean)
    def sharpen(self, amount, radius, luminance_only):
        width, height = self.engine.size
        mode, data = self.engine.image_data_as_rgb()
        imgdata = _sharpen.apply(
            mode, width, height, amount, radius,
            luminance_only, data
        )
        self.engine.set_image_data(imgdata)
