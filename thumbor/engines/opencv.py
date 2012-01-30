#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import cv

from thumbor.engines import BaseEngine

FORMATS = {
    '.jpg': 'JPEG',
    '.jpeg': 'JPEG',
    '.gif': 'GIF',
    '.png': 'PNG'
}

class Engine(BaseEngine):

    def create_image(self, buffer):
        # FIXME: opencv doesn't support gifs, even worse, the library
        # segfaults when trying to decoding a gif. An exception is a
        # less drastic measure.
        try:
            if FORMATS[self.extension] == 'GIF':
                raise ValueError("opencv doesn't support gifs")
        except KeyError:
            pass

        imagefiledata = cv.CreateMatHeader(1, len(buffer), cv.CV_8UC1)
        cv.SetData(imagefiledata, buffer, len(buffer))
        img0 = cv.DecodeImage(imagefiledata, cv.CV_LOAD_IMAGE_COLOR)

        return img0

    @property
    def size(self):
        return cv.GetSize(self.image)

    def normalize(self):
        pass

    def resize(self, width, height):
        thumbnail = cv.CreateMat(int(round(height, 0)), int(round(width, 0)), cv.CV_8UC3)
        cv.Resize(self.image, thumbnail)
        self.image = thumbnail

    def crop(self, left, top, right, bottom):
        new_width = right - left
        new_height = bottom - top
        cropped = cv.CreateImage((new_width, new_height), 8, 3)
        src_region = cv.GetSubRect(self.image, (left, top, new_width, new_height) )
        cv.Copy(src_region, cropped)

        self.image = cropped

    def flip_vertically(self):
        raise NotImplementedError()

    def flip_horizontally(self):
        raise NotImplementedError()

    def read(self, extension=None, quality=None):
        if quality is None: quality = self.context.request.quality
        options = None
        extension = extension or self.extension
        try:
            if FORMATS[extension] == 'JPEG':
               options = [cv.CV_IMWRITE_JPEG_QUALITY, quality]
        except KeyError:
            #default is JPEG so
            options = [cv.CV_IMWRITE_JPEG_QUALITY, quality]

        return cv.EncodeImage(extension, self.image, options or []).tostring()

    def get_image_data(self):
        return self.image.tostring()

    def set_image_data(self, data):
        cv.SetData(self.image, data)

    def get_image_mode(self):
        # TODO: Handle pngs with alpha channel
        return 'BGR'

    def draw_rectangle(self, x, y, width, height):
        cv.Rectangle(self.image, (x, y), (x + width, y + height), cv.Scalar(255, 255, 255, 1.0))
