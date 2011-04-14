#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from cStringIO import StringIO

from tornado.options import options

from thumbor.vendor.pythonmagickwand.image import Image
from thumbor.vendor.pythonmagickwand import wand
from thumbor.engines import BaseEngine

FORMATS = {
    '.jpg': 'JPEG',
    '.jpeg': 'JPEG',
    '.gif': 'GIF',
    '.png': 'PNG'
}

class Engine(BaseEngine):
    
    def create_image(self, buffer):
        return Image(StringIO(buffer))

    def resize(self, width, height):
        self.image.resize((int(width), int(height)), wand.CATROM_FILTER, 1)

    def crop(self, left, top, right, bottom):
        offset_left = left
        offset_top = top
        width = right - left
        height = bottom - top
        self.image.crop(
            (int(width), int(height)),
            (int(offset_left), int(offset_top))
        )

    def flip_vertically(self):
        self.image.flip()

    def flip_horizontally(self):
        self.image.flop()
    
    def read(self, extension):
        #returns image buffer in byte format.
        img_buffer = StringIO()
        self.image.format = FORMATS[extension]
        self.image.compression_quality = options.QUALITY
        self.image.save(img_buffer)
        results = img_buffer.getvalue()
        img_buffer.close()
        return results
