#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import splitext

import tornado.web
from tornado.options import define, options

from thumbor.transformer import Transformer
from thumbor.engines.json_engine import JSONEngine

define('ALLOWED_SOURCES', default=['www.globo.com', 's.glbimg.com'], multiple=True)
define('MAX_WIDTH', type=int, default=1280)
define('MAX_HEIGHT', type=int, default=1024)
define('QUALITY', type=int, default=80)

CONTENT_TYPE = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.png': 'image/png'
}

class BaseHandler(tornado.web.RequestHandler):
    def _error(self, status, msg=None):
        self.set_status(status)
        if msg is not None:
            self.write(msg)
        self.finish()

class MainHandler(BaseHandler):

    def initialize(self, loader, storage, engine, detectors):
        self.loader = loader
        self.storage = storage
        self.engine = engine
        self.detectors = detectors

    def _fetch(self, url, extension, callback):
        buffer = self.storage.get(url)

        if buffer is not None:
            callback(buffer)
        else:
            buffer = self.loader.load(url)
            if buffer is None:
                callback(None)
                return

            self.engine.load(buffer)
            self.engine.normalize()
            buffer = self.engine.read(extension)
            self.storage.put(url, buffer)
            callback(buffer)

    def validate(self, path):
        return self.loader.validate(path) if hasattr(self.loader, 'validate') else True

    @tornado.web.asynchronous
    def get(self,
            meta,
            crop_left,
            crop_top,
            crop_right,
            crop_bottom,
            should_flip_horizontal,
            width,
            should_flip_vertical,
            height,
            halign,
            valign,
            should_be_smart,
            path):

        meta = meta == "meta"

        if not self.validate(path):
            self._error(404)
            return

        should_crop = crop_left is not None
        if should_crop:
            crop_left = int(crop_left)
            crop_top = int(crop_top)
            crop_right = int(crop_right)
            crop_bottom = int(crop_bottom)

        width = int(width) if width else 0
        height = int(height) if height else 0

        if width > options.MAX_WIDTH:
            width = options.MAX_WIDTH
        if height > options.MAX_HEIGHT:
            height = options.MAX_HEIGHT

        if not halign:
            halign = 'center'
        if not valign:
            valign = 'middle'

        extension = splitext(path)[-1]

        def callback(buffer):
            if buffer is None:
                self._error(404)
                return

            context = dict(
                loader=self.loader,
                engine=self.engine,
                storage=self.storage,
                buffer=buffer,
                should_crop=should_crop,
                crop_left=crop_left,
                crop_top=crop_top,
                crop_right=crop_right,
                crop_bottom=crop_bottom,
                should_flip_horizontal=should_flip_horizontal,
                width=width,
                should_flip_vertical=should_flip_vertical,
                height=height,
                halign=halign,
                valign=valign,
                extension=extension,
                focal_points=[]
            )

            self.engine.load(buffer)

            if meta:
                context['engine'] = JSONEngine(self.engine, path)

            if self.detectors and should_be_smart:
                self.detectors[0](index=0, detectors=self.detectors).detect(context)

            Transformer(context).transform()

            if meta:
                self.set_header('Content-Type', "application/json")
            else:
                self.set_header('Content-Type', CONTENT_TYPE[context['extension']])

            results = context['engine'].read(context['extension'])

            self.write(results)
            self.finish()

        self._fetch(path, extension, callback)


class HealthcheckHandler(BaseHandler):
    def get(self):
        self.write('working')

