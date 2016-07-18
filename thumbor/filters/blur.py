# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import math

from thumbor.filters import BaseFilter, filter_method
from thumbor.ext.filters import _convolution

MAX_RADIUS = 150


class Filter(BaseFilter):
    """
        Usage: /filters:blur(<radius> [, <sigma>])
        Examples of use:
            /filters:blur(1)/
            /filters:blur(4)/
            /filters:blur(4, 2)/
    """

    def generate_1d_matrix(self, sigma, radius):
        matrix_size = (radius * 2) + 1
        matrix = []
        two_sigma_squared = float(2 * sigma * sigma)
        for x in xrange(matrix_size):
            adj_x = x - radius
            exp = math.e ** -(((adj_x * adj_x)) / two_sigma_squared)
            matrix.append(exp / math.sqrt(two_sigma_squared * math.pi))
        return tuple(matrix), matrix_size

    @filter_method(BaseFilter.PositiveNumber, BaseFilter.DecimalNumber)
    def blur(self, radius, sigma=0):
        if sigma == 0:
            sigma = radius
        if radius > MAX_RADIUS:
            radius = MAX_RADIUS
        matrix, matrix_size = self.generate_1d_matrix(sigma, radius)
        mode, data = self.engine.image_data_as_rgb()
        imgdata = _convolution.apply(mode, data, self.engine.size[0], self.engine.size[1], matrix, matrix_size, True)
        imgdata = _convolution.apply(mode, imgdata, self.engine.size[0], self.engine.size[1], matrix, 1, True)
        self.engine.set_image_data(imgdata)
