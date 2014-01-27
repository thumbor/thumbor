#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.filters import BaseFilter, filter_method
from thumbor.ext.filters import _fill


class Filter(BaseFilter):

    def get_median_color(self):
        r, g, b = _fill.apply(self.engine.get_image_mode(), self.engine.get_image_data())
        return '%02x%02x%02x' % (r, g, b)

    @filter_method(r'[\w]+')
    def fill(self, value):

        self.fill_engine = self.engine.__class__(self.context)
        bx = self.context.request.width if self.context.request.width != 0 else self.engine.image.size[0]
        by = self.context.request.height if self.context.request.height != 0 else self.engine.image.size[1]

        # if the value is 'auto'
        # we will calculate the median color of
        # all the pixels in the image and return
        if value == 'auto':
            value = self.get_median_color()

        try:
            self.fill_engine.image = self.fill_engine.gen_image((bx, by), value)
        except (ValueError, RuntimeError):
            self.fill_engine.image = self.fill_engine.gen_image((bx, by), '#%s' % value)

        ix, iy = self.engine.size

        px = (bx - ix) / 2  # top left
        py = (by - iy) / 2

        mergeValue = self.context.config.FILL_MERGES == true
        self.fill_engine.paste(self.engine, (px, py), merge=mergeValue)
        self.engine.image = self.fill_engine.image
