#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from tornado.options import options
from pgmagick import Image, Geometry, Blob, FilterTypes

from thumbor.engines import BaseEngine

FORMATS = {
    '.jpg': 'JPEG',
    '.jpeg': 'JPEG',
    '.gif': 'RGBA',
    '.png': 'PNG'
}

class Engine(BaseEngine):
    def create_image(self, buffer):
        blob = Blob(buffer)
        img = Image(blob)
        return img

    @property
    def size(self):
        size = self.image.size()

        return (size.width(), size.height())

    def resize(self, width, height):
        self.image.zoom('%dx%d'% (width,height))

    def crop(self, left, top, right, bottom):
        offset_left = left
        offset_top = top
        width = right - left
        height = bottom - top

        self.image.crop(
            Geometry(width, height, offset_left, offset_top)
        )

    def flip_vertically(self):
        self.image.flip()

    def flip_horizontally(self):
        self.image.flop()

    def read(self, extension=None, quality=options.QUALITY):
        #returns image buffer in byte format.
        img_buffer = Blob()

        ext = extension or self.extension
        self.image.magick(FORMATS[ext])

        self.image.quality(quality)

        #available_filters = ['BesselFilter', 'BlackmanFilter', 'BoxFilter', 'CatromFilter', 
                             #'CubicFilter', 'GaussianFilter', 'HammingFilter', 'HanningFilter',
                             #'HermiteFilter', 'LanczosFilter', 'MitchellFilter',
                             #'PointFilter', 'QuadraticFilter', 'SincFilter', 'TriangleFilter']

        f = FilterTypes.CatromFilter

        self.image.filterType(f)

        self.image.write(img_buffer)

        results = img_buffer.data

        return results
