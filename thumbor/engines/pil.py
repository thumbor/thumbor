#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from cStringIO import StringIO

from PIL import Image
from tornado.options import options

from thumbor.engines import BaseEngine

FORMATS = {
    '.jpg': 'JPEG',
    '.jpeg': 'JPEG',
    '.gif': 'GIF',
    '.png': 'PNG'
}

class Engine(BaseEngine):

    def create_image(self, buffer):
        return Image.open(StringIO(buffer))

    def resize(self, width, height):
        self.image = self.image.resize((int(width), int(height)), Image.ANTIALIAS)

    def crop(self, left, top, right, bottom):
        self.image = self.image.crop(
            (int(left),
            int(top),
            int(right),
            int(bottom))
        )

    def flip_vertically(self):
        self.image = self.image.transpose(Image.FLIP_TOP_BOTTOM)

    def flip_horizontally(self):
        self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)

    def read(self, extension=None, quality=options.QUALITY):
        #returns image buffer in byte format.
        img_buffer = StringIO()

        ext = extension or self.extension
        self.image.save(img_buffer, FORMATS[ext], quality=quality)

        results = img_buffer.getvalue()
        img_buffer.close()
        return results

