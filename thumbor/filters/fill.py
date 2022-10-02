#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.ext.filters import _fill
from thumbor.filters import BaseFilter, filter_method
from thumbor.filters.blur import apply_blur


class Filter(BaseFilter):
    def get_median_color(self):
        mode, data = self.engine.image_data_as_rgb()
        red, green, blue = _fill.apply(mode, data)
        return "%02x%02x%02x" % (  # pylint: disable=consider-using-f-string
            red,
            green,
            blue,
        )

    @filter_method(r"[\w]+", BaseFilter.Boolean)
    async def fill(self, color, fill_transparent=False):
        self.fill_engine = self.engine.__class__(self.context)
        target_width = (
            self.context.request.width
            if self.context.request.width != 0
            else self.engine.size[0]
        )
        target_height = (
            self.context.request.height
            if self.context.request.height != 0
            else self.engine.size[1]
        )

        # if the color is 'auto'
        # we will calculate the median color of
        # all the pixels in the image and return
        if color == "auto":
            color = self.get_median_color()

        if color == "blur":
            self.fill_engine.image = self.fill_engine.gen_image(
                self.engine.size, "transparent"
            )
            self.fill_engine.paste(self.engine, (0, 0))
            mode, data = self.fill_engine.image_data_as_rgb()
            data = apply_blur(mode, data, self.fill_engine.size, 50)
            self.fill_engine.set_image_data(data)
            self.fill_engine.resize(target_width, target_height)
        else:
            try:
                self.fill_engine.image = self.fill_engine.gen_image(
                    (target_width, target_height), color
                )
            except (ValueError, RuntimeError):
                self.fill_engine.image = self.fill_engine.gen_image(
                    (target_width, target_height), f"#{color}"
                )

        final_width, final_height = self.engine.size

        top_left_x = (target_width - final_width) // 2  # top left
        top_left_y = (target_height - final_height) // 2

        self.fill_engine.paste(
            self.engine, (top_left_x, top_left_y), merge=fill_transparent
        )
        self.engine.image = self.fill_engine.image
