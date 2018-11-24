#!/usr/bin/python
# -*- coding: utf-8 -*-
'''Filter Module'''

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com
from tornado import gen

from thumbor import Engine
from thumbor.filters import BaseFilter, filter_method


class Filter(BaseFilter):

    @gen.coroutine
    @filter_method()
    def upscale(self, details):
        target_width = details.target_width
        target_height = details.target_height

        source_width, source_height = yield Engine.get_image_size(self, details)

        if source_width >= target_width or source_height >= target_height:
            return

        if source_width * 1.0 / target_width >= source_height * 1.0 / target_height:
            new_width = target_width
            new_height = int(round(source_height * target_width / source_width))
        else:
            new_width = int(round(source_width * target_height / source_height))
            new_height = target_height

        yield Engine.resize(self, details, new_width, new_height)
