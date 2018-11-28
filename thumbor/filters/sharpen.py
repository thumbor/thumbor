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
from thumbor.ext.filters import _sharpen


class Filter(BaseFilter):

    @gen.coroutine
    @filter_method(BaseFilter.DecimalNumber, BaseFilter.DecimalNumber, BaseFilter.Boolean)
    def sharpen(self, details, amount, radius, luminance_only):
        width, height = yield Engine.get_image_size(self, details)

        mode, data = yield Engine.get_image_data_as_rgb(self, details)

        imgdata = _sharpen.apply(
            mode, width, height, amount, radius,
            luminance_only, data
        )

        yield Engine.set_image_data(self, details, imgdata)
