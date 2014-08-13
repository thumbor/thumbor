#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com


import thumbor.filters
from thumbor.filters import BaseFilter, filter_method


class Filter(BaseFilter):
    phase = thumbor.filters.PHASE_AFTER_LOAD

    @filter_method()
    def no_upscale(self):
        image_size = self.engine.size
        if self.context.request.width > image_size[0]:
            self.context.request.width = image_size[0]
        if self.context.request.height > image_size[1]:
            self.context.request.height = image_size[1]
