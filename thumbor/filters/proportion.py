#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.filters import BaseFilter, filter_method


class Filter(BaseFilter):
    @filter_method(BaseFilter.DecimalNumber)
    async def proportion(self, value):
        source_width, source_height = self.context.request.engine.size

        new_width = source_width * value
        new_height = source_height * value

        if new_width < 1 or new_height < 1:
            return

        self.engine.resize(new_width, new_height)
