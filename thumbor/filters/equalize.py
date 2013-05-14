#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.filters import BaseFilter, filter_method
from thumbor.ext.filters import _equalize


class Filter(BaseFilter):

    @filter_method()
    def equalize(self):
        imgdata = _equalize.apply(self.engine.get_image_mode(), self.engine.get_image_data())
        self.engine.set_image_data(imgdata)
