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

from thumbor.context import Context
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

    def init_request_params(self):
        self.context.request.quality = self.context.config.QUALITY
        self.context.request.url = self.request.path

    def execute_image_operations(self):
        self.init_request_params()

        req = self.context.request
        conf = self.context.config

        req.extension = splitext(req.image_url)[-1].lower()

        if self.context.modules.result_storage:
            result = self.context.modules.result_storage.get()
            if result is not None:
                logger.debug('[RESULT_STORAGE] IMAGE FOUND: %s' % req.url)
                self.finish_request(self.context, result)
                return

        req.should_crop = req.crop['left'] > 0 or \
                          req.crop['top'] > 0 or \
                          req.crop['right'] > 0 or \
                          req.crop['bottom'] > 0

        if conf.MAX_WIDTH and req.width > conf.MAX_WIDTH:
            req.width = conf.MAX_WIDTH
        if conf.MAX_HEIGHT and req.height > conf.MAX_HEIGHT:
            req.height = conf.MAX_HEIGHT

        req.meta_callback = conf.META_CALLBACK_NAME or self.request.arguments.get('callback', [None])[0]

        self.get_image()

    def get_image(self):
        def callback(normalized, buffer):
            if buffer is None:
                self._error(404)
                return

            engine = self.context.modules.engine
            req = self.context.request

            new_crops = None
            if normalized and req.should_crop:
                crop_left = req.crop['left']
                crop_top = req.crop['top']
                crop_right = req.crop['right']
                crop_bottom = req.crop['bottom']

                actual_width, actual_height = engine.size

                if not req.width and not req.height:
                    actual_width = engine.size[0]
                    actual_height = engine.size[1]
                elif req.width:
                    actual_height = engine.get_proportional_height(engine.size[0])
                elif req.height:
                    actual_width = engine.get_proportional_width(engine.size[1])

                new_crops = self.translate_crop_coordinates(
                    engine.source_width, 
                    engine.source_height, 
                    actual_width, 
                    actual_height, 
                    crop_left, 
                    crop_top, 
                    crop_right, 
                    crop_bottom
                )
                req.crop['left'] = new_crops[0]
                req.crop['top'] = new_crops[1]
                req.crop['right'] = new_crops[2]
                req.crop['bottom'] = new_crops[3]

            engine.load(buffer, req.extension)

            if req.meta:
                self.context.modules.engine = JSONEngine(engine, req.image_url, req.meta_callback)

            after_transform_cb = functools.partial(self.after_transform, self.context)
            Transformer(self.context).transform(after_transform_cb)

        self._fetch(self.context.request.image_url, self.context.request.extension, callback)

    def after_transform(self, context):
        finish_callback = functools.partial(self.finish_request, context)

        if context.modules.filters and context.request.filters:
            self.apply_filters(filters_module.create_instances(context, context.modules.filters, context.request.filters), finish_callback)
        else:
            finish_callback()

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

    def finish_request(self, context, result=None):
        if context.request.meta:
            content_type = 'text/javascript' if context.request.meta_callback else 'application/json'
        else:
            content_type = CONTENT_TYPE[context.request.extension]

        self.set_header('Content-Type', content_type)

        if result is None:
            results = context.modules.engine.read(context.request.extension, context.request.quality)
            if context.modules.result_storage: 
                context.modules.result_storage.put(results)
        else:
            results = result

        if context.request.detection_error is not None:
            self.set_status(404)

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
        if not hasattr(self.context.modules.loader, 'validate'):
            return True

        is_valid = self.context.modules.loader.validate(self.context, path)

        if not is_valid:
            logger.error('Request denied because the specified path "%s" was not identified by the loader as a valid path' % path)

        return is_valid

    def _fetch(self, url, extension, callback):
        storage = self.context.modules.storage
        buffer = storage.get(url)

        if buffer is not None:
            callback(False, buffer)
        else:
            def handle_loader_loaded(buffer):
                if buffer is None:
                    callback(False, None)
                    return

                engine = self.context.modules.engine
                engine.load(buffer, extension)
                normalized = engine.normalize()
                buffer = engine.read()

                storage.put(url, buffer)
                storage.put_crypto(url)

                callback(normalized, buffer)

            self.context.modules.loader.load(self.context, url, handle_loader_loaded)

class ContextHandler(BaseHandler):
    def initialize(self, context):
        self.context = Context(context.server, context.config, context.modules.importer)


