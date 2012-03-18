#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.filters import BaseFilter, filter_method

class Filter(BaseFilter):

    @filter_method(r'[\w]+')
    def fill(self, value):
        self.fill_engine = self.engine.__class__(self.context)
        bx = self.context.request.width if self.context.request.width != 0 else self.engine.image.size[0]
        by = self.context.request.height if self.context.request.height != 0 else self.engine.image.size[1]
        (ix, iy) = self.engine.image.size
        try:
            self.fill_engine.image = self.fill_engine.gen_image((bx,by), value)
        except (ValueError, RuntimeError):
            self.fill_engine.image = self.fill_engine.gen_image((bx,by), '#%s' % value)

        px = ( bx - ix ) / 2 #top left
        py = ( by - iy ) / 2


        self.fill_engine.paste(self.engine, (px, py))
        self.engine.image = self.fill_engine.image
