#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import functools
from os.path import splitext

import tornado.web
from tornado.options import options

from thumbor.transformer import Transformer
from thumbor.engines.json_engine import JSONEngine
from thumbor.utils import logger
from thumbor import filters as filters_module

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
        meta_callback = options.META_CALLBACK_NAME or self.request.arguments.get('callback', [None])[0]

        self.get_image(opt['debug'], opt['meta'], should_crop, crop_left,
                       crop_top, crop_right, crop_bottom,
                       opt['fit_in'],
                       opt['horizontal_flip'], width, opt['vertical_flip'],
                       height, halign, valign, extension,
                       opt['smart'], opt['filters'], meta_callback, image)

    def get_image(self,
                  debug,
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
                  filters_params,
                  meta_callback,
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
                meta=meta,
                loader=self.loader,
                engine=self.engine,
                storage=self.storage,
                detectors=self.detectors,
                normalized=normalized,
                debug=debug,
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
                filters=[],
                focal_points=[],
                quality=options.QUALITY,
                meta_callback=meta_callback,
                handler=self
            )

            self.engine.load(buffer, extension)

            if meta:
                context['engine'] = JSONEngine(self.engine, image, meta_callback)

            Transformer(context).transform()

            finish_callback = functools.partial(self.finish_request, context)

            if self.filters and filters_params:
                self.apply_filters(filters_module.create_instances(context, self.filters, filters_params), finish_callback)
            else:
                finish_callback()

        self._fetch(image, extension, callback)

    def apply_filters(self, filters, callback):
        if not filters:
            callback()
            return

        def exec_one_filter():
            if len(filters) == 0:
                callback()
                return

            f = filters.pop(0)
            if hasattr(f, 'run_filter'):
                f.run_filter()
                exec_one_filter()
            elif hasattr(f, 'run_filter_async'):
                f.run_filter_async(exec_one_filter)
        exec_one_filter()

    def finish_request(self, context):
        if context['meta']:
            content_type = 'text/javascript' if context['meta_callback'] else 'application/json'
        else:
            content_type = CONTENT_TYPE[context['extension']]

        self.set_header('Content-Type', content_type)

        results = context['engine'].read(context['extension'], context['quality'])

        self.write(results)
        self.finish()

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
        self.engine_class = engine.Engine
        self.loader = loader
        self.storage = storage.Storage()
        self.engine = self.engine_class()
        self.detectors = detectors
        self.filters = filters


