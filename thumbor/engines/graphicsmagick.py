#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pgmagick import Image, ImageType, Geometry, Blob, FilterTypes, Color, CompositeOperator as co
from pgmagick.api import Draw
from pgmagick._pgmagick import get_blob_data

from thumbor.engines import BaseEngine

FORMATS = {
    '.jpg': 'JPEG',
    '.jpeg': 'JPEG',
    '.gif': 'RGBA',
    '.png': 'PNG'
}

ALPHA_TYPES = [
    ImageType.GrayscaleMatteType,
    ImageType.PaletteMatteType,
    ImageType.TrueColorMatteType
]

class Engine(BaseEngine):

    def gen_image(self,size,color):
        if Color(str(color)).isValid():
            img = Image(Geometry(size[0], size[1]), Color(str(color)))
        else:
            raise ValueError
        return img

    def create_image(self, buffer):
        blob = Blob(buffer)
        img = Image(blob)
        return img

    @property
    def size(self):
        size = self.image.size()

        return (size.width(), size.height())

    def resize(self, width, height):
        self.image.zoom('%dx%d!'% (width,height))

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

    def read(self, extension=None, quality=None):
        if quality is None: quality = self.context.request.quality

        #returns image buffer in byte format.
        img_buffer = Blob()

        ext = extension or self.extension
        try:
            self.image.magick(FORMATS[ext])
        except KeyError:
            self.image.magick(FORMATS['.jpg'])

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

    def convert_to_rgb(self):
        return self.get_image_mode(), self.get_image_data()

    def get_image_data(self):
        self.image.magick(self.get_image_mode())
        blob = Blob()
        self.image.write(blob)
        data = get_blob_data(blob)
        return data

    def set_image_data(self, data):
        self.image.magick(self.get_image_mode())
        blob = Blob(data)
        self.image.size(self.image.size())
        self.image.read(blob)

    def get_image_mode(self):
        if self.image.type() in ALPHA_TYPES:
            return "RGBA"
        return "RGB"

    def draw_rectangle(self, x, y, width, height):
        draw = Draw()
        draw.fill_opacity(0.0)
        draw.stroke_color('white')
        draw.stroke_width(1)

        draw.rectangle(x, y, x + width, y + height)
        self.image.draw(draw.drawer)

    def paste(self, other_engine, pos, merge=True):
        self.enable_alpha()
        other_engine.enable_alpha()

        operator = co.OverCompositeOp if merge else co.CopyCompositeOp
        self.image.composite(other_engine.image, pos[0],pos[1], operator)

    def enable_alpha(self):
        self.image.type(ImageType.TrueColorMatteType)

    def strip_icc(self):
        self.image.iccColorProfile(Blob())
