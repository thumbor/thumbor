#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import splitext

import tornado.web
from tornado.options import options

from thumbor.transformer import Transformer
from thumbor.engines.json_engine import JSONEngine
from thumbor.utils import logger

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
            logger.error(msg)
        self.finish()

    def execute_image_operations(self, opt, image):

        should_crop = opt['crop']['left'] > 0 or \
                      opt['crop']['top'] > 0 or \
                      opt['crop']['right'] > 0 or \
                      opt['crop']['bottom'] > 0

        crop_left = crop_top = crop_right = crop_bottom = None
        if should_crop:
            crop_left = opt['crop']['left']
            crop_top = opt['crop']['top']
            crop_right = opt['crop']['right']
            crop_bottom = opt['crop']['bottom']

        width = opt['width']
        height = opt['height']

        if options.MAX_WIDTH and width > options.MAX_WIDTH:
            width = options.MAX_WIDTH
        if options.MAX_HEIGHT and height > options.MAX_HEIGHT:
            height = options.MAX_HEIGHT

        halign = opt['halign']
        valign = opt['valign']

        extension = splitext(image)[-1].lower()

        self.get_image(opt['meta'], should_crop, crop_left,
                       crop_top, crop_right, crop_bottom,
                       opt['fit_in'],
                       opt['horizontal_flip'], width, opt['vertical_flip'],
                       height, halign, valign, extension,
                       opt['smart'], image)

    def get_image(self,
                  meta,
                  should_crop,
                  crop_left,
                  crop_top,
                  crop_right,
                  crop_bottom,
                  fit_in,
                  horizontal_flip,
                  width,
                  vertical_flip,
                  height,
                  halign,
                  valign,
                  extension,
                  should_be_smart,
                  image
                  ):
        def callback(normalized, buffer):
            if buffer is None:
                self._error(404)
                return

            new_crops = None
            if normalized and should_crop:
                actual_width, actual_height = self.engine.size

                if not width and not height:
                    actual_width = self.engine.size[0]
                    actual_height = self.engine.size[1]
                elif width:
                    actual_height = self.engine.get_proportional_height(self.engine.size[0])
                elif height:
                    actual_width = self.engine.get_proportional_width(self.engine.size[1])

                new_crops = self.translate_crop_coordinates(
                    self.engine.source_width, 
                    self.engine.source_height, 
                    actual_width, 
                    actual_height, 
                    crop_left, 
                    crop_top, 
                    crop_right, 
                    crop_bottom
                )

            context = dict(
                loader=self.loader,
                engine=self.engine,
                storage=self.storage,
                detectors=self.detectors,
                normalized=normalized,
                buffer=buffer,
                should_crop=should_crop,
                crop_left=new_crops and new_crops[0] or crop_left,
                crop_top=new_crops and new_crops[1] or crop_top,
                crop_right=new_crops and new_crops[2] or crop_right,
                crop_bottom=new_crops and new_crops[3] or crop_bottom,
                fit_in=fit_in,
                should_flip_horizontal=horizontal_flip,
                width=width,
                should_flip_vertical=vertical_flip,
                height=height,
                halign=halign,
                valign=valign,
                smart=should_be_smart,
                image_url=image,
                extension=extension,
                focal_points=[]
            )

            self.engine.load(buffer, extension)

            if meta:
                context['engine'] = JSONEngine(self.engine, image)

            Transformer(context).transform()

            if meta:
                content_type = 'text/javascript' if options.META_CALLBACK_NAME else 'application/json'
            else:
                content_type = CONTENT_TYPE[context['extension']]

            self.set_header('Content-Type', content_type)

            results = context['engine'].read(context['extension'])

            self.write(results)
            self.finish()

        self._fetch(image, extension, callback)

    @classmethod
    def translate_crop_coordinates(cls, original_width, original_height, width, height, crop_left, crop_top, crop_right, crop_bottom):
        if original_width == width and original_height == height:
            return

        crop_left = crop_left * width / original_width
        crop_top = crop_top * height / original_height

        crop_right = crop_right * width / original_width
        crop_bottom = crop_bottom * height / original_height

        return (crop_left, crop_top, crop_right, crop_bottom)

    def validate(self, path):
        if not hasattr(self.loader, 'validate'):
            return True

        is_valid = self.loader.validate(path)

        if not is_valid:
            logger.error('Request denied because the specified path "%s" was not identified by the loader as a valid path' % path)

        return is_valid

    def _fetch(self, url, extension, callback):
        storage = self.storage
        buffer = storage.get(url)

        if buffer is not None:
            callback(False, buffer)
        else:
            def handle_loader_loaded(buffer):
                if buffer is None:
                    callback(False, None)
                    return

                self.engine.load(buffer, extension)
                normalized = self.engine.normalize()
                buffer = self.engine.read()

                storage.put(url, buffer)
                storage.put_crypto(url)

                callback(normalized, buffer)

            self.loader.load(url, handle_loader_loaded)

class ContextHandler(BaseHandler):
    def initialize(self, loader, storage, engine, detectors, filters):
        self.loader = loader
        self.storage = storage.Storage()
        self.engine = engine.Engine()
        self.detectors = detectors
        self.filters = filters


