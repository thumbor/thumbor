#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.filters import BaseFilter, filter_method


class Filter(BaseFilter):
    @filter_method(r"[\w]+")
    async def background_color(self, color):
        self.fill_engine = self.engine.__class__(self.context)
        width, height = self.engine.size
        try:
            self.fill_engine.image = self.fill_engine.gen_image(
                (width, height), color
            )
        except (ValueError, RuntimeError):
            self.fill_engine.image = self.fill_engine.gen_image(
                (width, height), f"#{color}"
            )
        self.fill_engine.paste(self.engine, (0, 0), merge=True)
        self.engine.image = self.fill_engine.image
