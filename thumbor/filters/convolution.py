# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.filters import BaseFilter, filter_method
from thumbor.ext.filters import _convolution


class Filter(BaseFilter):
    """
        Usage: /filters:convolution(<semicolon separated matrix items>, <number of columns in matrix>, <should normalize boolean>)
        Example of blur filter: /filters:convolution(1;2;1;2;4;2;1;2;1,3,true)/
    """

    @filter_method(r'(?:[-]?[\d]+\.?[\d]*[;])*(?:[-]?[\d]+\.?[\d]*)', BaseFilter.PositiveNumber, BaseFilter.Boolean)
    def convolution(self, matrix, columns, should_normalize=True):
        matrix = tuple(matrix.split(';'))
        mode, data = self.engine.image_data_as_rgb()
        imgdata = _convolution.apply(mode, data, self.engine.size[0], self.engine.size[1], matrix, columns, should_normalize)
        self.engine.set_image_data(imgdata)
