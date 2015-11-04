#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import splitext
from thumbor.ext.filters import _alpha
from thumbor.filters import BaseFilter, filter_method
from thumbor.loaders import LoaderResult
import tornado.gen


class Filter(BaseFilter):
    regex = r'(?:watermark\((?P<url>.*?),(?P<x>-?[\d]*?),(?P<y>-?[\d]*?),(?P<alpha>[\d]*?)\))'

    def on_image_ready(self, buffer):

        self.watermark_engine.load(buffer, self.extension)
        self.watermark_engine.enable_alpha()

        mode, data = self.watermark_engine.image_data_as_rgb()
        imgdata = _alpha.apply(mode,
                               self.alpha,
                               data)

        self.watermark_engine.set_image_data(imgdata)

        inv_x = self.x[0] == '-'
        inv_y = self.y[0] == '-'
        x, y = int(self.x), int(self.y)

        sz = self.engine.size
        watermark_sz = self.watermark_engine.size
        if inv_x:
            x = (sz[0] - watermark_sz[0]) + x
        if inv_y:
            y = (sz[1] - watermark_sz[1]) + y

        self.engine.paste(self.watermark_engine, (x, y), merge=True)

        self.callback()

    def on_fetch_done(self, result):
        # TODO if result.successful is False how can the error be handled?
        if isinstance(result, LoaderResult):
            buffer = result.buffer
        else:
            buffer = result

        self.watermark_engine.load(buffer, self.extension)
        self.storage.put(self.url, self.watermark_engine.read())
        self.storage.put_crypto(self.url)
        self.on_image_ready(buffer)

    @filter_method(BaseFilter.String, r'-?[\d]+', r'-?[\d]+', BaseFilter.PositiveNumber, async=True)
    @tornado.gen.coroutine
    def watermark(self, callback, url, x, y, alpha):
        self.url = url
        self.x = x
        self.y = y
        self.alpha = alpha
        self.callback = callback
        self.extension = splitext(self.url)[-1].lower()
        self.watermark_engine = self.context.modules.engine.__class__(self.context)
        self.storage = self.context.modules.storage

        buffer = yield tornado.gen.maybe_future(self.storage.get(self.url))
        if buffer is not None:
            self.on_image_ready(buffer)
        else:
            self.context.modules.loader.load(self.context, self.url, self.on_fetch_done)
