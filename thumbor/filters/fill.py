#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.filters import BaseFilter, filter_method
from thumbor.ext.filters import _fill


class Filter(BaseFilter):

    def get_median_color(self):
        mode, data = self.engine.image_data_as_rgb()
        r, g, b = _fill.apply(mode, data)
        return '%02x%02x%02x' % (r, g, b)

    @filter_method(r'[\w]+', BaseFilter.Boolean)
    def fill(self, color, fill_transparent=False):
        self.fill_engine = self.engine.__class__(self.context)
        bx = self.context.request.width if self.context.request.width != 0 else self.engine.size[0]
        by = self.context.request.height if self.context.request.height != 0 else self.engine.size[1]

        # if the color is 'auto'
        # we will calculate the median color of
        # all the pixels in the image and return
        if color == 'auto':
            color = self.get_median_color()

        try:
            self.fill_engine.image = self.fill_engine.gen_image((bx, by), color)
        except (ValueError, RuntimeError):
            self.fill_engine.image = self.fill_engine.gen_image((bx, by), '#%s' % color)

        ix, iy = self.engine.size

        px = (bx - ix) / 2  # top left
        py = (by - iy) / 2

        self.fill_engine.paste(self.engine, (px, py), merge=fill_transparent)
        self.engine.image = self.fill_engine.image
