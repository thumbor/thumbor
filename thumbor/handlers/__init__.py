#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import sys
import functools
from os.path import splitext
import datetime
import traceback

import tornado.web

from thumbor import __version__
from thumbor.storages.no_storage import Storage as NoStorage
from thumbor.storages.mixed_storage import Storage as MixedStorage
from thumbor.context import Context
from thumbor.transformer import Transformer
from thumbor.engines import BaseEngine
from thumbor.engines.gif import Engine as GifEngine
from thumbor.engines.json_engine import JSONEngine
from thumbor.utils import logger
import thumbor.filters

CONTENT_TYPE = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.png': 'image/png',
    '.webp': 'image/webp'
}


class BaseHandler(tornado.web.RequestHandler):
    def _error(self, status, msg=None):
        self.set_status(status)
        if msg is not None:
            logger.warn(msg)
        self.finish()

    def execute_image_operations(self):
        self.context.request.quality = None

        req = self.context.request
        conf = self.context.config

        req.extension = splitext(req.image_url)[-1].lower()

        should_store = self.context.config.RESULT_STORAGE_STORES_UNSAFE or not self.context.request.unsafe
        if self.context.modules.result_storage and should_store:
          if self.context.request.purge:
            self.context.modules.result_storage.remove()
            logger.debug('[RESULT_STORAGE] IMAGE PURGED: %s' % req.url)
            self.set_status(204)
            self.finish()
            return
          else:
            result = self.context.modules.result_storage.get()
            if result is not None:
                mime = BaseEngine.get_mimetype(result)
                if mime == '.gif' and self.context.config.USE_GIFSICLE_ENGINE:
                    self.context.request.engine = GifEngine(self.context)
                else:
                    self.context.request.engine = self.context.modules.engine

                logger.debug('[RESULT_STORAGE] IMAGE FOUND: %s' % req.url)
                self.finish_request(self.context, result)
                return

        if conf.MAX_WIDTH and (not isinstance(req.width, basestring)) and req.width > conf.MAX_WIDTH:
            req.width = conf.MAX_WIDTH
        if conf.MAX_HEIGHT and (not isinstance(req.height, basestring)) and req.height > conf.MAX_HEIGHT:
            req.height = conf.MAX_HEIGHT

        req.meta_callback = conf.META_CALLBACK_NAME or self.request.arguments.get('callback', [None])[0]

        self.filters_runner = self.context.filters_factory.create_instances(self.context, self.context.request.filters)
        self.filters_runner.apply_filters(thumbor.filters.PHASE_PRE_LOAD, self.get_image)

    def get_image(self):
        def callback(normalized, buffer=None, engine=None):
            req = self.context.request

            if engine is None:
                if buffer is None:
                    self._error(404)
                    return

                engine = self.context.request.engine
                engine.load(buffer, req.extension)

            self.normalize_crops(normalized, req, engine)

            if req.meta:
                self.context.request.engine = JSONEngine(engine, req.image_url, req.meta_callback)

            after_transform_cb = functools.partial(self.after_transform, self.context)
            Transformer(self.context).transform(after_transform_cb)

        self._fetch(self.context.request.image_url, self.context.request.extension, callback)

    def normalize_crops(self, normalized, req, engine):
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

    def after_transform(self, context):
        finish_callback = functools.partial(self.finish_request, context)
        if context.request.extension == '.gif' and context.config.USE_GIFSICLE_ENGINE:
            finish_callback()
        else:
            self.filters_runner.apply_filters(thumbor.filters.PHASE_POST_TRANSFORM, finish_callback)

    def define_image_type(self, context, result):
        if result is not None:
            image_extension = BaseEngine.get_mimetype(result)
        else:
            image_extension = context.request.format
            if image_extension is not None:
                image_extension = '.%s' % image_extension
                logger.debug('Image format specified as %s.' % image_extension)
            elif context.config.AUTO_WEBP and context.request.accepts_webp and not context.request.engine.is_multiple():
                image_extension = '.webp'
                logger.debug('Image format set by AUTO_WEBP as %s.' % image_extension)
            else:
                image_extension = context.request.engine.extension
                logger.debug('No image format specified. Retrieving from the image extension: %s.' % image_extension)

        content_type = CONTENT_TYPE.get(image_extension, CONTENT_TYPE['.jpg'])

        if context.request.meta:
            context.request.meta_callback = context.config.META_CALLBACK_NAME or self.request.arguments.get('callback', [None])[0]
            content_type = 'text/javascript' if context.request.meta_callback else 'application/json'
            logger.debug('Metadata requested. Serving content type of %s.' % content_type)

        logger.debug('Content Type of %s detected.' % content_type)

        return image_extension, content_type

    def finish_request(self, context, result=None):
        image_extension, content_type = self.define_image_type(context, result)

        quality = self.context.request.quality
        if quality is None:
            if image_extension == '.webp':
                quality = self.context.config.get('WEBP_QUALITY', self.context.config.QUALITY)
            else:
                quality = self.context.config.QUALITY

        self.set_header('Content-Type', content_type)
        self.set_header('Server', 'Thumbor/%s' % __version__)

        if context.config.AUTO_WEBP and not context.request.engine.is_multiple() and context.request.engine.extension != '.webp':
            self.set_header('Vary', 'Accept')

        max_age = self.context.config.MAX_AGE
        if context.request.prevent_result_storage or context.request.detection_error:
            max_age = self.context.config.MAX_AGE_TEMP_IMAGE

        if max_age:
            self.set_header('Cache-Control', 'max-age=' + str(max_age) + ',public')
            self.set_header('Expires', datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age))

        # needs to be decided before loading results from the engine
        should_store = result is None and (context.config.RESULT_STORAGE_STORES_UNSAFE or not context.request.unsafe)

        if result is None:
            results = context.request.engine.read(image_extension, quality)
            if context.request.max_bytes is not None:
                results = self.reload_to_fit_in_kb(
                    context.request.engine,
                    results,
                    image_extension,
                    quality,
                    context.request.max_bytes
                )
        else:
            results = result

        self.write(results)
        self.finish()

        if should_store:
            if context.modules.result_storage and not context.request.prevent_result_storage:
                context.modules.result_storage.put(results)

    def reload_to_fit_in_kb(self, engine, initial_results, extension, initial_quality, max_bytes):
        if extension not in ['.webp', '.jpg', '.jpeg'] or len(initial_results) <= max_bytes:
            return initial_results

        results = initial_results
        quality = initial_quality

        while len(results) > max_bytes:
            quality = int(quality * 0.75)

            if quality < 10:
                logger.debug('Could not find any reduction that matches required size of %d bytes.' % max_bytes)
                return initial_results

            logger.debug('Trying to downsize image with quality of %d...' % quality)
            results = engine.read(extension, quality)

        prev_result = results
        while len(results) <= max_bytes:
            quality = int(quality * 1.1)
            logger.debug('Trying to upsize image with quality of %d...' % quality)
            prev_result = results
            results = engine.read(extension, quality)

        return prev_result

    @classmethod
    def translate_crop_coordinates(
            cls,
            original_width,
            original_height,
            width,
            height,
            crop_left,
            crop_top,
            crop_right,
            crop_bottom):

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
            logger.warn('Request denied because the specified path "%s" was not identified by the loader as a valid path' % path)

        return is_valid

    def _fetch(self, url, extension, callback):
        storage = self.context.modules.storage
        buffer = storage.get(url)

        if buffer is not None:
            mime = BaseEngine.get_mimetype(buffer)
            if mime == '.gif' and self.context.config.USE_GIFSICLE_ENGINE:
                self.context.request.engine = GifEngine(self.context)
            else:
                self.context.request.engine = self.context.modules.engine

            callback(False, buffer=buffer)
        else:
            def handle_loader_loaded(buffer):
                if buffer is None:
                    callback(False, None)
                    return

                original_preserve = self.context.config.PRESERVE_EXIF_INFO
                self.context.config.PRESERVE_EXIF_INFO = True

                try:
                    mime = BaseEngine.get_mimetype(buffer)

                    if mime == '.gif' and self.context.config.USE_GIFSICLE_ENGINE:
                        self.context.request.engine = GifEngine(self.context)
                    else:
                        self.context.request.engine = self.context.modules.engine

                    self.context.request.engine.load(buffer, extension)
                    normalized = self.context.request.engine.normalize()
                    is_no_storage = isinstance(storage, NoStorage)
                    is_mixed_storage = isinstance(storage, MixedStorage)
                    is_mixed_no_file_storage = is_mixed_storage and isinstance(storage.file_storage, NoStorage)

                    if not (is_no_storage or is_mixed_no_file_storage):
                        buffer = self.context.request.engine.read()
                        storage.put(url, buffer)

                    storage.put_crypto(url)
                finally:
                    self.context.config.PRESERVE_EXIF_INFO = original_preserve

                callback(normalized, engine=self.context.request.engine)

            self.context.modules.loader.load(self.context, url, handle_loader_loaded)


class ContextHandler(BaseHandler):
    def initialize(self, context):
        self.context = Context(context.server, context.config, context.modules.importer, self)

    def log_exception(self, *exc_info):
        if isinstance(exc_info[1], tornado.web.HTTPError):
            # Delegate HTTPError's to the base class
            # We don't want these through normal exception handling
            return super(ContextHandler, self).log_exception(*exc_info)

        msg = traceback.format_exception(*exc_info)

        try:
            if self.context.config.USE_CUSTOM_ERROR_HANDLING:
                self.context.modules.importer.error_handler.handle_error(context=self.context, handler=self, exception=exc_info)
        finally:
            del exc_info
            logger.error('ERROR: %s' % "".join(msg))


##
# Base handler for Image API operations
##
class ImageApiHandler(ContextHandler):

    def validate(self, body):
        conf = self.context.config
        mime = BaseEngine.get_mimetype(body)

        if mime == '.gif' and self.context.config.USE_GIFSICLE_ENGINE:
            engine = GifEngine(self.context)
        else:
            engine = self.context.modules.engine

        # Check if image is valid
        try:
            engine.load(body, None)
        except IOError:
            self._error(415, 'Unsupported Media Type')
            return False

        # Check weight constraints
        if (conf.UPLOAD_MAX_SIZE != 0 and len(self.request.body) > conf.UPLOAD_MAX_SIZE):
            self._error(
                412,
                'Image exceed max weight (Expected : %s, Actual : %s)' % (conf.UPLOAD_MAX_SIZE, len(self.request.body)))
            return False

        # Check size constraints
        size = engine.size
        if (conf.MIN_WIDTH > size[0] or conf.MIN_HEIGHT > size[1]):
            self._error(
                412,
                'Image is too small (Expected: %s/%s , Actual : %s/%s) % (conf.MIN_WIDTH, conf.MIN_HEIGHT, size[0], size[1])')
            return False
        return True

    def write_file(self, id, body):
        storage = self.context.modules.upload_photo_storage
        storage.put(id, body)
