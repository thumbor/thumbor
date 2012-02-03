#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.filters import BaseFilter
from PIL import Image

class Filter(BaseFilter):
    regex = r'(?:fill\((?P<value>[\w]+)\))'

    def run_filter(self):
        self.fill_engine = self.engine.__class__(self.context)
        bx = self.context.request.width
        by = self.context.request.height
        (ix, iy) = self.engine.image.size
        try:
            self.fill_engine.image = self.fill_engine.gen_image((bx,by),self.params['value'])
        except (ValueError,RuntimeError):
            self.fill_engine.image = self.fill_engine.gen_image((bx,by),'#' + self.params['value'])

        px = ( bx - ix )/2 #top left
        py = ( by - iy )/2
	
        self.fill_engine.paste(self.engine, (px, py))
        self.engine.image = self.fill_engine.image
