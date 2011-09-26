#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.filters import BaseFilter
import math

class Filter(BaseFilter):
    regex = r'(?:contrast\((?P<value>[-]?[\d]+)\))'

    def run_filter(self, imgdata):
        delta = math.pow((int(self.params['value']) + 100) / 100.0, 2)
        l = list(imgdata)
        sz = len(l)
        for i in xrange(0, sz, 3):
            r = ord(l[i])
            g = ord(l[i + 1])
            b = ord(l[i + 2])

            r = r / 255.0
            r -= 0.5
            r *= delta
            r += 0.5
            r *= 255

            g = g / 255.0
            g -= 0.5
            g *= delta
            g += 0.5
            g *= 255

            b = b / 255.0
            b -= 0.5
            b *= delta
            b += 0.5
            b *= 255

            if r > 255: r = 255
            if r < 0: r = 0
            if g > 255: g = 255
            if g < 0: g = 0
            if b > 255: b = 255
            if b < 0: b = 0
            l[i] = chr(r)
            l[i + 1] = chr(g)
            l[i + 2] = chr(b)
        return ''.join(l)
