# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import tornado.web

from thumbor.ext.filters import _convolution
from thumbor.filters import BaseFilter, filter_method

# pylint: disable=line-too-long

MAX_CONVOLUTION_KERNEL_SIDE = 15
MAX_CONVOLUTION_KERNEL_ELEMENTS = (
    MAX_CONVOLUTION_KERNEL_SIDE * MAX_CONVOLUTION_KERNEL_SIDE
)
MAX_CONVOLUTION_WORK = 1_000_000_000


def validate_convolution_work(width, height, kernel_size):
    if width * height * kernel_size > MAX_CONVOLUTION_WORK:
        raise tornado.web.HTTPError(
            400, reason="Convolution kernel is too expensive"
        )


def validate_custom_kernel(matrix_size, columns, width, height):
    if columns <= 0:
        raise tornado.web.HTTPError(400, reason="Invalid convolution columns")

    rows, remainder = divmod(matrix_size, columns)
    if (
        remainder
        or rows > MAX_CONVOLUTION_KERNEL_SIDE
        or columns > MAX_CONVOLUTION_KERNEL_SIDE
        or matrix_size > MAX_CONVOLUTION_KERNEL_ELEMENTS
    ):
        raise tornado.web.HTTPError(
            400, reason="Convolution kernel dimensions are too large"
        )
    validate_convolution_work(width, height, matrix_size)


class Filter(BaseFilter):
    """
    Usage: /filters:convolution(<semicolon separated matrix items>, <number of columns in matrix>, <should normalize boolean>)
    Example of blur filter: /filters:convolution(1;2;1;2;4;2;1;2;1,3,true)/
    """

    @filter_method(
        r"-?\d+(?:\.\d*)?(?:;-?\d+(?:\.\d*)?)*",
        BaseFilter.PositiveNonZeroNumber,
        BaseFilter.Boolean,
    )
    async def convolution(self, matrix, columns, should_normalize=True):
        matrix = tuple(matrix.split(";"))
        mode, data = self.engine.image_data_as_rgb()
        validate_custom_kernel(
            len(matrix),
            columns,
            self.engine.size[0],
            self.engine.size[1],
        )
        imgdata = _convolution.apply(
            mode,
            data,
            self.engine.size[0],
            self.engine.size[1],
            matrix,
            columns,
            should_normalize,
        )
        self.engine.set_image_data(imgdata)
