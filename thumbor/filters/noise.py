#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.filters import BaseFilter
from thumbor.ext.filters import _noise

class Filter(BaseFilter):
    regex = r'(?:noise\((?P<amount>[\d]+)\))'

    def run_filter(self):
        imgdata = _noise.apply(self.engine.get_image_mode(), int(self.params['amount']), self.engine.get_image_data())
        self.engine.set_image_data(imgdata)
