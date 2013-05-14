#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.ext.filters import _nine_patch
from thumbor.filters import BaseFilter, filter_method
from os.path import splitext


class Filter(BaseFilter):
    regex = r'(?:frame\((?P<url>.*?))'

    def on_image_ready(self, buffer):
        self.nine_patch_engine.load(buffer, self.extension)
        self.nine_patch_engine.enable_alpha()
        self.engine.enable_alpha()

        padding = _nine_patch.get_padding(self.nine_patch_engine.get_image_mode(),
                                          self.nine_patch_engine.get_image_data(),
                                          self.nine_patch_engine.size[0],
                                          self.nine_patch_engine.size[1])

        self.handle_padding(padding)

        if self.engine.get_image_mode() != self.nine_patch_engine.get_image_mode():
            raise RuntimeError('Image mode mismatch: %s != %s' % (
                self.engine.get_image_mode(), self.nine_patch_engine.get_image_mode())
            )

        imgdata = _nine_patch.apply(self.engine.get_image_mode(),
                                    self.engine.get_image_data(),
                                    self.engine.size[0],
                                    self.engine.size[1],
                                    self.nine_patch_engine.get_image_data(),
                                    self.nine_patch_engine.size[0],
                                    self.nine_patch_engine.size[1])
        self.engine.set_image_data(imgdata)
        self.callback()

    def handle_padding(self, padding):
        '''Pads the image with transparent pixels if necessary.'''
        left = padding[0]
        top = padding[1]
        right = padding[2]
        bottom = padding[3]

        offset_x = 0
        offset_y = 0
        new_width = self.engine.size[0]
        new_height = self.engine.size[1]

        if left > 0:
            offset_x = left
            new_width += left
        if top > 0:
            offset_y = top
            new_height += top
        if right > 0:
            new_width += right
        if bottom > 0:
            new_height += bottom
        new_engine = self.context.modules.engine.__class__(self.context)
        new_engine.image = new_engine.gen_image((new_width, new_height), '#fff')
        new_engine.enable_alpha()
        new_engine.image.paste(self.engine.image, (offset_x, offset_y))
        self.engine.image = new_engine.image

    def on_fetch_done(self, buffer):
        self.nine_patch_engine.load(buffer, self.extension)
        self.storage.put(self.url, self.nine_patch_engine.read())
        self.storage.put_crypto(self.url)
        self.on_image_ready(buffer)

    @filter_method(BaseFilter.String, async=True)
    def frame(self, callback, url):
        self.url = url
        self.callback = callback
        self.extension = splitext(self.url)[-1].lower()
        self.nine_patch_engine = self.context.modules.engine.__class__(self.context)
        self.storage = self.context.modules.storage

        buffer = self.storage.get(self.url)
        if buffer is not None:
            self.on_image_ready(buffer)
        else:
            self.context.modules.loader.load(self.context, self.url, self.on_fetch_done)
