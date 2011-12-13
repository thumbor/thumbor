#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.filters import BaseFilter
from thumbor.ext.filters import _round_corner

class Filter(BaseFilter):
    regex = r'(?:round_corner\((?P<a_radius>[\d]+)(?:\|(?P<b_radius>[\d]+))?,(?P<r>[\d]+),(?P<g>[\d]+),(?P<b>[\d]+)\))'

    def run_filter(self):
        width, height = self.engine.size
        a_radius = int(self.params['a_radius'])
        b_radius = self.params.get('b_radius', None)
        if b_radius:
            b_radius = int(b_radius)
        else:
            b_radius = a_radius

        imgdata = _round_corner.apply(1, self.engine.get_image_mode(), a_radius, b_radius, int(self.params['r']), int(self.params['g']), int(self.params['b']), width, height, self.engine.get_image_data())
        self.engine.set_image_data(imgdata)
