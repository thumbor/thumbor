#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.filters import BaseFilter
from thumbor.ext.filters import _rgb

class Filter(BaseFilter):
    regex = r'(?:rgb\((?P<r>[-]?[\d]+),(?P<g>[-]?[\d]+),(?P<b>[-]?[\d]+)\))'

    def run_filter(self, imgdata, engine):
        return _rgb.apply(int(self.params['r']), int(self.params['g']), int(self.params['b']), imgdata)
