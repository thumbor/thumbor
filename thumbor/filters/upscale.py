#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.filters import BaseFilter, filter_method


class Filter(BaseFilter):
    @filter_method()
    async def upscale(self):
        target_width = self.context.request.width
        target_height = self.context.request.height

        source_width, source_height = self.context.request.engine.size

        if source_width >= target_width or source_height >= target_height:
            return

        if (
            source_width * 1.0 / target_width
            >= source_height * 1.0 / target_height
        ):
            new_width = target_width
            new_height = int(source_height * target_width / source_width)
        else:
            new_width = int(source_width * target_height / source_height)
            new_height = target_height

        self.engine.resize(new_width, new_height)
