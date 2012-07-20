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
from thumbor.utils import logger

# frame(ninepatch,x,y,w,h)
# ninepatch: URL
# x: int; frame top-left corner offset.
# y: int;
# w: int; frame width & height.
# h: int;

class Filter(BaseFilter):
    regex = r'(?:frame\((?P<url>.*?),(?P<x>-?[\d]*?),(?P<y>-?[\d]*?),(?P<w>-?[\d]*?),(?P<h>-?[\d]*?))'

    def on_image_ready(self, buffer):
        logger.warn('Image ready %d %d.' % (self.x, self.y))

        # TODO: if the bounds of the frame exceed the bounds of the image, resize the image

        self.nine_patch_engine.load(buffer, self.extension)
        self.nine_patch_engine.enable_alpha()
        self.engine.enable_alpha()

        if self.engine.get_image_mode() != self.nine_patch_engine.get_image_mode():
            raise RuntimeError('Image mode mismatch: %s != %s' % (self.engine.get_image_mode(), self.nine_patch_engine.get_image_mode()))

        imgdata = _nine_patch.apply(self.engine.get_image_mode(),
                                    self.engine.get_image_data(),
                                    self.engine.size[0],
                                    self.engine.size[1],
                                    self.nine_patch_engine.get_image_data(),
                                    self.nine_patch_engine.size[0],
                                    self.nine_patch_engine.size[1])
        self.engine.set_image_data(imgdata)
        self.callback()

    def on_fetch_done(self, buffer):
        self.nine_patch_engine.load(buffer, self.extension)
        self.storage.put(self.url, self.nine_patch_engine.read())
        self.storage.put_crypto(self.url)
        self.on_image_ready(buffer)

    @filter_method(BaseFilter.String, BaseFilter.Number, BaseFilter.Number, BaseFilter.Number, BaseFilter.Number, async = True)
    def frame(self, callback, url, x, y, w, h):
        self.url = url
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.callback = callback
        self.extension = splitext(self.url)[-1].lower()
        self.nine_patch_engine = self.context.modules.engine.__class__(self.context)
        self.storage = self.context.modules.storage

        buffer = self.storage.get(self.url)
        if buffer is not None:
            self.on_image_ready(buffer)
        else:
            self.context.modules.loader.load(self.context, self.url, self.on_fetch_done)
