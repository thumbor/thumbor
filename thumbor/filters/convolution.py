#!/usr/bin/python
# -*- coding: utf-8 -*-
'''Filter Module'''

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from tornado import gen

from thumbor import Engine
from thumbor.ext.filters import _convolution
from thumbor.filters import BaseFilter, filter_method


class Filter(BaseFilter):
    """
        Usage: /filters:convolution(<semicolon separated matrix items>, <number of columns in matrix>, <should normalize boolean>)
        Example of blur filter: /filters:convolution(1;2;1;2;4;2;1;2;1,3,true)/
    """

    @gen.coroutine
    @filter_method(r'(?:[-]?[\d]+\.?[\d]*[;])*(?:[-]?[\d]+\.?[\d]*)', BaseFilter.PositiveNumber, BaseFilter.Boolean)
    def convolution(self, details, matrix, columns, should_normalize=True):
        matrix = tuple(matrix.split(';'))
        mode, data = yield Engine.get_image_data_as_rgb(self, details)

        width, height = yield Engine.get_image_size(self, details)
        imgdata = _convolution.apply(
            mode, data, width, height, matrix, columns, should_normalize)
        yield Engine.set_image_data(self, details, imgdata)
