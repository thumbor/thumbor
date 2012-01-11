#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from cStringIO import StringIO

from PIL import Image, ImageFile, ImageDraw

from thumbor.engines import BaseEngine
from thumbor.utils import logger

FORMATS = {
    '.jpg': 'JPEG',
    '.jpeg': 'JPEG',
    '.gif': 'GIF',
    '.png': 'PNG'
}

ImageFile.MAXBLOCK = 2**25

class Engine(BaseEngine):

    def create_image(self, buffer):
        img = Image.open(StringIO(buffer))
        self.icc_profile = img.info.get('icc_profile', None)
        return img

    def draw_rectangle(self, x, y, width, height):
        d = ImageDraw.Draw(self.image)
        d.rectangle([x, y, x + width, y + height])
        del d

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

    def read(self, extension=None, quality=None):
        if quality is None: quality = self.context.request.quality
        #returns image buffer in byte format.
        img_buffer = StringIO()

        ext = extension or self.extension
        options = {
            'quality': quality
        }
        if ext == '.jpg' or ext == '.jpeg':
            options['optimize'] = True
            options['progressive'] = True

        if self.icc_profile is not None:
            options['icc_profile'] = self.icc_profile

        try:
            self.image.save(img_buffer, FORMATS[ext], **options)
        except IOError:
            logger.warning('Could not save as improved image, consider to increase ImageFile.MAXBLOCK')
            self.image.save(img_buffer, FORMATS[ext])

        results = img_buffer.getvalue()
        img_buffer.close()
        return results

    def get_image_data(self):
        return self.image.tostring()

    def set_image_data(self, data):
        self.image.fromstring(data)

    def get_image_mode(self):
        return self.image.mode

    def paste(self, other_engine, pos):
        image = self.image
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        other_image = other_engine.image
        if other_image.mode != 'RGBA':
            other_image = other_image.convert('RGBA')

        layer = Image.new('RGBA', image.size, (0,0,0,0))
        layer.paste(other_image, pos)
        self.image = Image.composite(layer, image, layer)
