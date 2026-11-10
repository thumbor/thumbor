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
        source_width, source_height = self.engine.size
        target_width, target_height = self.target_size(
            source_width, source_height
        )

        if source_width >= target_width or source_height >= target_height:
            return

        if self.width_leads(
            source_width, source_height, target_width, target_height
        ):
            new_width = target_width
            new_height = int(source_height * target_width / source_width)
        else:
            new_width = int(source_width * target_height / source_height)
            new_height = target_height

        self.engine.resize(new_width, new_height)

    def width_leads(
        self, source_width, source_height, target_width, target_height
    ):
        request = self.context.request
        if not request.height:
            return True
        if not request.width:
            return False
        return source_width / target_width >= source_height / target_height

    def target_size(self, source_width, source_height):
        request = self.context.request
        width = source_width if request.width == "orig" else request.width
        height = source_height if request.height == "orig" else request.height
        if not width and not height:
            return source_width, source_height
        if not width:
            width = source_width * height / source_height
        if not height:
            height = source_height * width / source_width
        return width, height
