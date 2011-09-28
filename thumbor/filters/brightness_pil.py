#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.filters import BaseFilter
from thumbor.ext.filters import _brightness
import math

class Filter(BaseFilter):
    regex = r'(?:brightness_pil\((?P<value>[-]?[\d]+)\))'

    def run_filter(self, imgdata, engine):
        delta = (int(self.params['value']) + 100.0) / 100.0
        engine.brightness(delta)
