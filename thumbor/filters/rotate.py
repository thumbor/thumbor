#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.filters import BaseFilter, filter_method


class Filter(BaseFilter):

    @filter_method(r'90|180|270|exif')
    def rotate(self, value):
        if value == 'exif':
            self.engine.reorientate()
        else:
            value = int(value) % 360 # To optimize for engines
            self.engine.rotate(value)
