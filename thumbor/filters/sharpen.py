#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.filters import BaseFilter, filter_method
from thumbor.ext.filters import _sharpen


class Filter(BaseFilter):

    @filter_method(BaseFilter.DecimalNumber, BaseFilter.DecimalNumber, BaseFilter.Boolean)
    def sharpen(self, amount, radius, luminance_only):
        width, height = self.engine.size
        imgdata = _sharpen.apply(
            self.engine.get_image_mode(), width, height, amount, radius,
            luminance_only, self.engine.get_image_data()
        )
        self.engine.set_image_data(imgdata)
