#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.ext.filters import _alpha
from thumbor.filters import BaseFilter, filter_method
from thumbor.loaders import LoaderResult
from thumbor.utils import logger
import tornado.gen
import math
import re


class Filter(BaseFilter):

    @staticmethod
    def detect_and_get_ratio_position(pos, length):
        match = re.match('^(-?)([0-9]+)p$', pos)

        if not match:
            return pos

        sign, ratio = match.groups()
        pos = "{sign}{pos}".format(sign=sign, pos=int(round(length * float(ratio) / 100, 0)))

        return pos

    @staticmethod
    def calc_watermark_size(sz, watermark_sz, w_ratio, h_ratio):
        wm_max_width = sz[0] * w_ratio if w_ratio else None
        wm_max_height = sz[1] * h_ratio if h_ratio else None

        if not wm_max_width:
            wm_max_width = watermark_sz[0] * wm_max_height / watermark_sz[1]

        if not wm_max_height:
            wm_max_height = watermark_sz[1] * wm_max_width / watermark_sz[0]

        if float(watermark_sz[0]) / wm_max_width >= float(watermark_sz[1]) / wm_max_height:
            wm_height = round(watermark_sz[1] * wm_max_width / watermark_sz[0])
            wm_width = round(wm_max_width)
        else:
            wm_height = round(wm_max_height)
            wm_width = round(watermark_sz[0] * wm_max_height / watermark_sz[1])

        return (wm_width, wm_height)

    def on_image_ready(self, buffer):
        self.watermark_engine.load(buffer, None)
        self.watermark_engine.enable_alpha()

        mode, data = self.watermark_engine.image_data_as_rgb()
        imgdata = _alpha.apply(mode,
                               self.alpha,
                               data)

        self.watermark_engine.set_image_data(imgdata)

        sz = self.engine.size
        watermark_sz = self.watermark_engine.size

        if self.w_ratio or self.h_ratio:
            watermark_sz = self.calc_watermark_size(sz, watermark_sz, self.w_ratio, self.h_ratio)
            self.watermark_engine.resize(watermark_sz[0], watermark_sz[1])

        self.x = self.detect_and_get_ratio_position(self.x, sz[0])
        self.y = self.detect_and_get_ratio_position(self.y, sz[1])

        mos_x = self.x == 'repeat'
        mos_y = self.y == 'repeat'
        center_x = self.x == 'center'
        center_y = self.y == 'center'
        if not center_x and not mos_x:
            inv_x = self.x[0] == '-'
            x = int(self.x)
        if not center_y and not mos_y:
            inv_y = self.y[0] == '-'
            y = int(self.y)

        if not mos_x:
            repeat_x = (1, 0)
            if center_x:
                x = (sz[0] - watermark_sz[0]) / 2
            elif inv_x:
                x = (sz[0] - watermark_sz[0]) + x
        else:
            repeat_x = divmod(sz[0], watermark_sz[0])
            if sz[0] * 1.0 / watermark_sz[0] < 2:
                repeat_x = (math.ceil(sz[0] * 1.0 / watermark_sz[0]), 10)
                space_x = 10
        if not mos_y:
            repeat_y = (1, 0)
            if center_y:
                y = (sz[1] - watermark_sz[1]) / 2
            elif inv_y:
                y = (sz[1] - watermark_sz[1]) + y
        else:
            repeat_y = divmod(sz[1], watermark_sz[1])
            if sz[1] * 1.0 / watermark_sz[1] < 2:
                repeat_y = (math.ceil(sz[1] * 1.0 / watermark_sz[1]), 10)
                space_y = 10

        if not mos_x and not mos_y:
            self.engine.paste(self.watermark_engine, (x, y), merge=True)
        elif mos_x and mos_y:
            if (repeat_x[0] * repeat_y[0]) > 100:
                tmpRepeatX = min(6, repeat_x[0])
                tmpRepeatY = min(6, repeat_y[0])
                repeat_x = (tmpRepeatX, sz[0] - tmpRepeatX * watermark_sz[0])
                repeat_y = (tmpRepeatY, sz[1] - tmpRepeatY * watermark_sz[1])
            space_x = repeat_x[1] / (max(repeat_x[0], 2) - 1)
            space_y = repeat_y[1] / (max(repeat_y[0], 2) - 1)
            for i in range(int(repeat_x[0])):
                x = i * space_x + i * watermark_sz[0]
                for j in range(int(repeat_y[0])):
                    y = j * space_y + j * watermark_sz[1]
                    self.engine.paste(self.watermark_engine, (x, y), merge=True)
        elif mos_x:
            space_x = repeat_x[1] / (max(repeat_x[0], 2) - 1)
            for i in range(int(repeat_x[0])):
                x = i * space_x + i * watermark_sz[0]
                self.engine.paste(self.watermark_engine, (x, y), merge=True)
        else:
            space_y = repeat_y[1] / (max(repeat_y[0], 2) - 1)
            for j in range(int(repeat_y[0])):
                y = j * space_y + j * watermark_sz[1]
                self.engine.paste(self.watermark_engine, (x, y), merge=True)

        self.callback()

    def on_fetch_done(self, result):
        if not result.successful:
            logger.warn(
                'bad watermark result error=%s metadata=%s' %
                (result.error, result.metadata)
            )
            raise tornado.web.HTTPError(400)

        if isinstance(result, LoaderResult):
            buffer = result.buffer
        else:
            buffer = result

        self.watermark_engine.load(buffer, None)
        self.storage.put(self.url, self.watermark_engine.read())
        self.storage.put_crypto(self.url)
        self.on_image_ready(buffer)

    @tornado.gen.coroutine
    @filter_method(
        BaseFilter.String,
        r'(?:-?\d+p?)|center|repeat',
        r'(?:-?\d+p?)|center|repeat',
        BaseFilter.PositiveNumber,
        r'(?:-?\d+)|none',
        r'(?:-?\d+)|none',
        async=True
    )
    def watermark(self, callback, url, x, y, alpha, w_ratio=False, h_ratio=False):
        self.url = url
        self.x = x
        self.y = y
        self.alpha = alpha
        self.w_ratio = float(w_ratio) / 100.0 if w_ratio and w_ratio != 'none' else False
        self.h_ratio = float(h_ratio) / 100.0 if h_ratio and h_ratio != 'none' else False
        self.callback = callback
        self.watermark_engine = self.context.modules.engine.__class__(self.context)
        self.storage = self.context.modules.storage

        try:
            buffer = yield tornado.gen.maybe_future(self.storage.get(self.url))
            if buffer is not None:
                self.on_image_ready(buffer)
            else:
                self.context.modules.loader.load(self.context, self.url, self.on_fetch_done)
        except Exception as e:
            logger.exception(e)
            logger.warn("bad watermark")
            raise tornado.web.HTTPError(500)
