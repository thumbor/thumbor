# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import math

from thumbor.ext.filters import _convolution
from thumbor.filters import BaseFilter, filter_method

MAX_RADIUS = 150


def generate_1d_matrix(sigma, radius):
    matrix_size = (radius * 2) + 1
    matrix = []
    two_sigma_squared = float(2 * sigma * sigma)
    for column in range(matrix_size):
        adj_x = column - radius
        exp = math.e ** -(((adj_x * adj_x)) / two_sigma_squared)
        matrix.append(exp / math.sqrt(two_sigma_squared * math.pi))
    return tuple(matrix), matrix_size


def apply_blur(mode, data, size, radius, sigma=0):
    if sigma == 0:
        sigma = radius
    radius = min(radius, MAX_RADIUS)
    matrix, matrix_size = generate_1d_matrix(sigma, radius)
    data = _convolution.apply(
        mode, data, size[0], size[1], matrix, matrix_size, True
    )
    return _convolution.apply(mode, data, size[0], size[1], matrix, 1, True)


class Filter(BaseFilter):
    """
    Usage: /filters:blur(<radius> [, <sigma>])
    Examples of use:
        /filters:blur(1)/
        /filters:blur(4)/
        /filters:blur(4, 2)/
    """

    @filter_method(BaseFilter.PositiveNonZeroNumber, BaseFilter.DecimalNumber)
    async def blur(self, radius, sigma=0):
        mode, imgdata = self.engine.image_data_as_rgb()
        imgdata = apply_blur(mode, imgdata, self.engine.size, radius, sigma)
        self.engine.set_image_data(imgdata)
