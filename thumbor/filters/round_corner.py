#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.filters import BaseFilter, filter_method
from thumbor.ext.filters import _round_corner


class Filter(BaseFilter):

    @filter_method(r'[\d]+(?:\|[\d]+)?', BaseFilter.PositiveNumber, BaseFilter.PositiveNumber, BaseFilter.PositiveNumber)
    def round_corner(self, radius, r, g, b):
        width, height = self.engine.size
        radius_parts = radius.split('|')
        a_radius = int(radius_parts[0])
        b_radius = int(radius_parts[1]) if len(radius_parts) > 1 else a_radius

        imgdata = _round_corner.apply(
            1, self.engine.get_image_mode(), a_radius, b_radius, r, g, b,
            width, height, self.engine.get_image_data()
        )
        self.engine.set_image_data(imgdata)
