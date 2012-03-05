#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.filters import BaseFilter
from thumbor.ext.filters import _sharpen

class Filter(BaseFilter):
    regex = r'(?:sharpen\((?P<amount>[\d]+(?:\.\d+)?),(?P<radius>[\d]+(?:\.\d+)?),(?P<luminance_only>true|false)\))'

    def run_filter(self):
        width, height = self.engine.size
        luminance_only = self.params['amount'] == 'true'
        imgdata = _sharpen.apply(self.engine.get_image_mode(), width, height, float(self.params['amount']), float(self.params['radius']), luminance_only, self.engine.get_image_data())
        self.engine.set_image_data(imgdata)
