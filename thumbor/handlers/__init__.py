#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import sys
import functools
import datetime
import pytz
import traceback

import tornado.web
import tornado.gen as gen
from tornado.locks import Condition

from thumbor import __version__
from thumbor.context import Context
from thumbor.engines import BaseEngine
from thumbor.engines.json_engine import JSONEngine
from thumbor.loaders import LoaderResult
from thumbor.media import Media
from thumbor.result_storages import ResultStorageResult
from thumbor.storages.no_storage import Storage as NoStorage
from thumbor.storages.mixed_storage import Storage as MixedStorage
from thumbor.transformer import Transformer
from thumbor.utils import logger, CONTENT_TYPE, EXTENSION
import thumbor.filters


HTTP_DATE_FMT = "%a, %d %b %Y %H:%M:%S GMT"


class FetchResult(object):

    def __init__(self, normalized=False, media=None, engine=None, successful=False, loader_error=None):
        self.normalized = normalized
        self.engine = engine
        self.media = media
        self.successful = successful
        self.loader_error = loader_error


class BaseHandler(tornado.web.RequestHandler):
    url_locks = {}

    def _error(self, status, msg=None):
        self.set_status(status)
        if msg is not None:
            logger.warn(msg)
        self.finish()

    @gen.coroutine
    def execute_image_operations(self):
        self.context.request.quality = None

        req = self.context.request
        conf = self.context.config

        should_store = self.context.config.RESULT_STORAGE_STORES_UNSAFE or not self.context.request.unsafe

        if self.context.modules.result_storage and should_store:
            start = datetime.datetime.now()

            result = yield gen.maybe_future(self.context.modules.result_storage.get())

            finish = datetime.datetime.now()

            self.context.metrics.timing('result_storage.incoming_time', (finish - start).total_seconds() * 1000)

            media = None

            if result is None:
                self.context.metrics.incr('result_storage.miss')
            else:
                media = Media.from_result(result)

                self.context.metrics.incr('result_storage.hit')
                self.context.metrics.incr('result_storage.bytes_read', len(result))

            if media is not None:
                mime = BaseEngine.get_mimetype(media.buffer)

                if mime == 'image/gif' and self.context.config.USE_GIFSICLE_ENGINE:
                    self.context.request.engine = self.context.modules.gif_engine
                else:
                    self.context.request.engine = self.context.modules.engine

                self.context.request.engine.load(media.buffer, EXTENSION.get(mime, '.jpg'))

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

    @gen.coroutine  # NOQA
    def get_image(self):
        try:
            result = yield self._fetch(
                self.context.request.image_url
            )

            if not result.successful:
                if result.loader_error == LoaderResult.ERROR_NOT_FOUND:
                    self._error(404)
                    return
                elif result.loader_error == LoaderResult.ERROR_UPSTREAM:
                    # Return a Bad Gateway status if the error came from upstream
                    self._error(502)
                    return
                elif result.loader_error == LoaderResult.ERROR_TIMEOUT:
                    # Return a Gateway Timeout status if upstream timed out (i.e. 599)
                    self._error(504)
                    return
                else:
                    self._error(500)
                    return

        except Exception as e:
            msg = '[BaseHandler] get_image failed for url `{url}`. error: `{error}`'.format(
                url=self.context.request.image_url,
                error=e
            )

            self.log_exception(*sys.exc_info())

            if 'cannot identify image file' in e.message:
                logger.warning(msg)
                self._error(400)
            else:
                logger.error(msg)
                self._error(500)
            return

        normalized = result.normalized

        media = result.media

        engine = result.engine

        req = self.context.request

        if engine is None:
            if media.buffer is None:
                self._error(504)
                return

            engine = self.context.request.engine

            try:
                engine.load(media.buffer, self.context.request.extension)
            except Exception:
                self._error(504)
                return

        def transform():
            self.normalize_crops(normalized, req, engine)

            if req.meta:
                self.context.request.engine = JSONEngine(engine, req.image_url, req.meta_callback)

            after_transform_cb = functools.partial(self.after_transform, self.context)
            Transformer(self.context).transform(after_transform_cb)

        self.filters_runner.apply_filters(thumbor.filters.PHASE_AFTER_LOAD, transform)

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

    def is_webp(self, context):
        return (context.config.AUTO_WEBP and
                context.request.accepts_webp and
                not context.request.engine.is_multiple() and
                context.request.engine.can_convert_to_webp())

    def define_image_type(self, context, result):
        if result is not None:
            media = Media.from_result(result)

            image_extension = EXTENSION.get(BaseEngine.get_mimetype(media.buffer), '.jpg')
        else:
            image_extension = context.request.format
            if image_extension is not None:
                image_extension = '.%s' % image_extension
                logger.debug('Image format specified as %s.' % image_extension)
            elif self.is_webp(context):
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

        return (image_extension, content_type)

    def _load_media(self, context):
        image_extension, content_type = self.define_image_type(context, None)

        quality = self.context.request.quality
        if quality is None:
            if image_extension == '.webp' and self.context.config.WEBP_QUALITY is not None:
                quality = self.context.config.get('WEBP_QUALITY')
            else:
                quality = self.context.config.QUALITY

        media = Media(context.request.engine.read(image_extension, quality))

        if context.request.max_bytes is not None:
            media = Media(self.reload_to_fit_in_kb(
                context.request.engine,
                media.buffer,
                image_extension,
                quality,
                context.request.max_bytes
            ))

        if not context.request.meta:
            media = self.optimize(context, media)
            # An optimizer might have modified the image format.
            media.metadata.update({'ContentType': BaseEngine.get_mimetype(media.buffer)})

        return media

    @gen.coroutine
    def _process_result_from_storage(self, result):
        if self.context.config.SEND_IF_MODIFIED_LAST_MODIFIED_HEADERS:
            # Handle If-Modified-Since & Last-Modified header
            try:
                if isinstance(result, ResultStorageResult):
                    result_last_modified = result.last_modified
                else:
                    result_last_modified = yield gen.maybe_future(self.context.modules.result_storage.last_updated())

                if result_last_modified:
                    if 'If-Modified-Since' in self.request.headers:
                        date_modified_since = datetime.datetime.strptime(
                            self.request.headers['If-Modified-Since'], HTTP_DATE_FMT
                        ).replace(tzinfo=pytz.utc)

                        if result_last_modified <= date_modified_since:
                            self.set_status(304)
                            self.finish()
                            return

                    self.set_header('Last-Modified', result_last_modified.strftime(HTTP_DATE_FMT))
            except NotImplementedError:
                logger.warn('last_updated method is not supported by your result storage service, hence If-Modified-Since & '
                            'Last-Updated headers support is disabled.')

    @gen.coroutine
    def finish_request(self, context, media_from_storage=None):
        if media_from_storage is not None:
            self._process_result_from_storage(media_from_storage)

            image_extension, content_type = self.define_image_type(context, media_from_storage)

            media_from_storage.metadata.update({
                'ContentType': content_type,
                'FileExtension': image_extension
            })

            self._write_media_to_client(context, media_from_storage)
            return

        should_store = media_from_storage is None and (
            context.config.RESULT_STORAGE_STORES_UNSAFE or not context.request.unsafe)

        def inner(future):
            media = future.result()

            image_extension, content_type = self.define_image_type(context, media_from_storage)

            media.metadata.update({
                'ContentType': content_type,
                'FileExtension': image_extension
            })

            self._write_media_to_client(context, media)

            if should_store:
                self._store_media(context, media)

        self.context.thread_pool.queue(
            operation=functools.partial(self._load_media, context),
            callback=inner,
        )

    def _write_media_to_client(self, context, media):
        max_age = context.config.MAX_AGE

        if context.request.max_age is not None:
            max_age = context.request.max_age

        if context.request.prevent_result_storage or context.request.detection_error:
            max_age = context.config.MAX_AGE_TEMP_IMAGE

        if max_age:
            self.set_header('Cache-Control', 'max-age=' + str(max_age) + ',public')
            self.set_header('Expires', datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age))

        self.set_header('Server', 'Thumbor/%s' % __version__)
        self.set_header('Content-Type', media.content_type)

        if context.config.AUTO_WEBP and \
                not context.request.engine.is_multiple() and \
                context.request.engine.can_convert_to_webp() and \
                context.request.engine.extension != '.webp':
            self.set_header('Vary', 'Accept')

        context.headers = self._headers.copy()

        self.write(media.buffer)
        self.finish()

    def _store_media(self, context, media):
        if not context.modules.result_storage or context.request.prevent_result_storage:
            return

        @gen.coroutine
        def save_to_result_storage():
            start = datetime.datetime.now()

            if context.modules.result_storage.is_media_aware:
                yield gen.maybe_future(context.modules.result_storage.put(media))
            else:
                yield gen.maybe_future(context.modules.result_storage.put(media.buffer))

            finish = datetime.datetime.now()
            context.metrics.incr('result_storage.bytes_written', len(media.buffer))
            context.metrics.timing('result_storage.outgoing_time', (finish - start).total_seconds() * 1000)

        tornado.ioloop.IOLoop.instance().add_callback(save_to_result_storage)

    def optimize(self, context, media):
        for optimizer in context.modules.optimizers:
            if optimizer.is_media_aware:
                result = optimizer(context).run_optimizer(media)

                if result:
                    media = result

            else:
                buffer = optimizer(context).run_optimizer(
                    media.metadata.get('FileExtension', None),
                    media.buffer
                )
                if buffer is not None:
                    media = Media(buffer)

        return media

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

    @gen.coroutine
    def _fetch(self, url):
        fetch_result = FetchResult()

        storage = self.context.modules.storage

        yield self.acquire_url_lock(url)

        try:
            storage_result = yield gen.maybe_future(storage.get(url))

            fetch_result.media = Media.from_result(storage_result)
            mime = None


            if fetch_result.media.buffer is not None:
                self.context.metrics.incr('storage.hit')

                fetch_result.successful = True
                mime = BaseEngine.get_mimetype(fetch_result.media.buffer)
                self.context.request.extension = EXTENSION.get(mime, '.jpg')

                if mime == 'image/gif' and self.context.config.USE_GIFSICLE_ENGINE:
                    self.context.request.engine = self.context.modules.gif_engine
                else:
                    self.context.request.engine = self.context.modules.engine

                raise gen.Return(fetch_result)
            else:
                self.context.metrics.incr('storage.miss')

            loader_result = yield self.context.modules.loader.load(self.context, url)
        finally:
            self.release_url_lock(url)

        fetch_result.media = Media.from_result(loader_result)
        if not fetch_result.media.is_valid:
            raise gen.Return(fetch_result)

        fetch_result.successful = True

        if mime is None:
            mime = BaseEngine.get_mimetype(fetch_result.media.buffer)

        self.context.request.extension = EXTENSION.get(mime, '.jpg')

        original_preserve = self.context.config.PRESERVE_EXIF_INFO
        self.context.config.PRESERVE_EXIF_INFO = True

        try:
            mime = BaseEngine.get_mimetype(fetch_result.media.buffer)
            self.context.request.extension = extension = EXTENSION.get(mime, None)

            if mime == 'image/gif' and self.context.config.USE_GIFSICLE_ENGINE:
                self.context.request.engine = self.context.modules.gif_engine
            else:
                self.context.request.engine = self.context.modules.engine

            self.context.request.engine.load(fetch_result.media.buffer, extension)

            fetch_result.normalized = self.context.request.engine.normalize()

            # Allows engine or loader to override storage on the fly for the purpose of
            # marking a specific file as unstoreable
            storage = self.context.modules.storage

            is_no_storage = isinstance(storage, NoStorage)
            is_mixed_storage = isinstance(storage, MixedStorage)
            is_mixed_no_file_storage = is_mixed_storage and isinstance(storage.file_storage, NoStorage)

            if not (is_no_storage or is_mixed_no_file_storage):
                fetch_result.media = Media(self.context.request.engine.read(extension))

                if storage.is_media_aware:
                    storage.put(url, fetch_result.media)
                else:
                    storage.put(url, fetch_result.media.buffer)

            storage.put_crypto(url)
        finally:
            self.context.config.PRESERVE_EXIF_INFO = original_preserve

        fetch_result.media = None
        fetch_result.engine = self.context.request.engine

        raise gen.Return(fetch_result)

    @gen.coroutine
    def get_blacklist_contents(self):
        filename = 'blacklist.txt'

        exists = yield gen.maybe_future(self.context.modules.storage.exists(filename))

        if exists:
            result = yield gen.maybe_future(self.context.modules.storage.get(filename))
            raise tornado.gen.Return(Media.from_result(result).buffer)
        else:
            raise tornado.gen.Return("")

    @gen.coroutine
    def acquire_url_lock(self, url):
        if not url in BaseHandler.url_locks:
            BaseHandler.url_locks[url] = Condition()
        else:
            yield BaseHandler.url_locks[url].wait()

    def release_url_lock(self, url):
        try:
            BaseHandler.url_locks[url].notify_all()
            del BaseHandler.url_locks[url]
        except KeyError:
            pass


class ContextHandler(BaseHandler):
    def initialize(self, context):
        self.context = Context(
            server=context.server,
            config=context.config,
            importer=context.modules.importer,
            request_handler=self
        )

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

        if mime == 'image/gif' and self.context.config.USE_GIFSICLE_ENGINE:
            engine = self.context.modules.gif_engine
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
        if storage.is_media_aware:
            storage.put(id, Media(body))
        else:
            storage.put(id, body)
