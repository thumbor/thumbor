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
from thumbor.ext.filters import _round_corner


class Filter(BaseFilter):

    @gen.coroutine
    @filter_method(r'[\d]+(?:\|[\d]+)?', BaseFilter.PositiveNumber, BaseFilter.PositiveNumber, BaseFilter.PositiveNumber)
    def round_corner(self, details, radius, r, g, b):
        width, height = yield Engine.get_image_size(self, details)
        radius_parts = radius.split('|')
        a_radius = int(radius_parts[0])
        b_radius = int(radius_parts[1]) if len(radius_parts) > 1 else a_radius

        mode, data = yield Engine.get_image_data_as_rgb(self, details)
        imgdata = _round_corner.apply(
            1, mode, a_radius, b_radius, r, g, b,
            width, height, data
        )
        yield Engine.set_image_data(self, details, imgdata)
