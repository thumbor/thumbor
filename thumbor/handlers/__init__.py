#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import sys
import functools
import datetime
import re
import pytz
import traceback

import tornado.web
import tornado.gen as gen
from tornado.locks import Condition

from thumbor import __version__
from thumbor.context import Context
from thumbor.engines import BaseEngine, EngineResult
from thumbor.engines.json_engine import JSONEngine
from thumbor.loaders import LoaderResult
from thumbor.result_storages import ResultStorageResult
from thumbor.storages.no_storage import Storage as NoStorage
from thumbor.storages.mixed_storage import Storage as MixedStorage
from thumbor.transformer import Transformer
from thumbor.utils import logger, CONTENT_TYPE, EXTENSION
import thumbor.filters


HTTP_DATE_FMT = "%a, %d %b %Y %H:%M:%S GMT"


class FetchResult(object):

    def __init__(self, normalized=False, buffer=None, engine=None, successful=False, loader_error=None):
        self.normalized = normalized
        self.engine = engine
        self.buffer = buffer
        self.successful = successful
        self.loader_error = loader_error


class BaseHandler(tornado.web.RequestHandler):
    url_locks = {}

    def prepare(self, *args, **kwargs):
        super(BaseHandler, self).prepare(*args, **kwargs)

        if not hasattr(self, 'context'):
            return

        self._response_ext = None
        self._response_length = None

        self._response_start = datetime.datetime.now()
        self.context.metrics.incr('response.count')

    def on_finish(self, *args, **kwargs):
        super(BaseHandler, self).on_finish(*args, **kwargs)

        if not hasattr(self, 'context'):
            return

        total_time = (datetime.datetime.now() - self._response_start).total_seconds() * 1000
        status = self.get_status()
        self.context.metrics.timing('response.time', total_time)
        self.context.metrics.timing('response.time.{0}'.format(status), total_time)
        self.context.metrics.incr('response.status.{0}'.format(status))

        if self._response_ext is not None:
            ext = self._response_ext
            self.context.metrics.incr('response.format{0}'.format(ext))
            self.context.metrics.timing('response.time{0}'.format(ext), total_time)
            if self._response_length is not None:
                self.context.metrics.incr('response.bytes{0}'.format(ext), self._response_length)

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

            if result is None:
                self.context.metrics.incr('result_storage.miss')
            else:
                self.context.metrics.incr('result_storage.hit')
                self.context.metrics.incr('result_storage.bytes_read', len(result))
                logger.debug('[RESULT_STORAGE] IMAGE FOUND: %s' % req.url)
                self.finish_request(self.context, result)
                return

        if conf.MAX_WIDTH and (not isinstance(req.width, basestring)) and req.width > conf.MAX_WIDTH:
            req.width = conf.MAX_WIDTH
        if conf.MAX_HEIGHT and (not isinstance(req.height, basestring)) and req.height > conf.MAX_HEIGHT:
            req.height = conf.MAX_HEIGHT

        req.meta_callback = conf.META_CALLBACK_NAME or self.request.arguments.get('callback', [None])[0]

        self.filters_runner = self.context.filters_factory.create_instances(self.context, self.context.request.filters)
        # Apply all the filters from the PRE_LOAD phase and call get_image() afterwards.
        self.filters_runner.apply_filters(thumbor.filters.PHASE_PRE_LOAD, self.get_image)

    @gen.coroutine  # NOQA
    def get_image(self):
        """
        This function is called after the PRE_LOAD filters have been applied.
        It applies the AFTER_LOAD filters on the result, then crops the image.
        """
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
                elif result.engine_error == EngineResult.COULD_NOT_LOAD_IMAGE:
                    self._error(400)
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
        buffer = result.buffer
        engine = result.engine

        req = self.context.request

        if engine is None:
            if buffer is None:
                self._error(504)
                return

            engine = self.context.request.engine
            try:
                engine.load(buffer, self.context.request.extension)
            except Exception:
                self._error(504)
                return

        self.context.transformer = Transformer(self.context)

        def transform():
            self.normalize_crops(normalized, req, engine)

            if req.meta:
                self.context.transformer.engine = \
                    self.context.request.engine = \
                    JSONEngine(engine, req.image_url, req.meta_callback)

            after_transform_cb = functools.partial(self.after_transform, self.context)
            self.context.transformer.transform(after_transform_cb)

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

    def is_animated_gif(self, data):
        if data[:6] not in [b"GIF87a", b"GIF89a"]:
            return False
        i = 10  # skip header
        frames = 0

        def skip_color_table(i, flags):
            if flags & 0x80:
                i += 3 << ((flags & 7) + 1)
            return i

        flags = ord(data[i])
        i = skip_color_table(i + 3, flags)
        while frames < 2:
            block = data[i]
            i += 1
            if block == b'\x3B':
                break
            if block == b'\x21':
                i += 1
            elif block == b'\x2C':
                frames += 1
                i += 8
                i = skip_color_table(i + 1, ord(data[i]))
                i += 1
            else:
                return False
            while True:
                l = ord(data[i])
                i += 1
                if not l:
                    break
                i += l
        return frames > 1

    def define_image_type(self, context, result):
        if result is not None:
            if isinstance(result, ResultStorageResult):
                buffer = result.buffer
            else:
                buffer = result
            image_extension = EXTENSION.get(BaseEngine.get_mimetype(buffer), '.jpg')
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

    def _load_results(self, context):
        image_extension, content_type = self.define_image_type(context, None)

        quality = self.context.request.quality
        if quality is None:
            if image_extension == '.webp' and self.context.config.WEBP_QUALITY is not None:
                quality = self.context.config.get('WEBP_QUALITY')
            else:
                quality = self.context.config.QUALITY
        results = context.request.engine.read(image_extension, quality)
        if context.request.max_bytes is not None:
            results = self.reload_to_fit_in_kb(
                context.request.engine,
                results,
                image_extension,
                quality,
                context.request.max_bytes
            )
        if not context.request.meta:
            results = self.optimize(context, image_extension, results)
            # An optimizer might have modified the image format.
            content_type = BaseEngine.get_mimetype(results)

        return results, content_type

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
    def finish_request(self, context, result_from_storage=None):
        if result_from_storage is not None:
            self._process_result_from_storage(result_from_storage)

            image_extension, content_type = self.define_image_type(context, result_from_storage)
            self._write_results_to_client(context, result_from_storage, content_type)

            return

        should_store = result_from_storage is None and (
            context.config.RESULT_STORAGE_STORES_UNSAFE or not context.request.unsafe)

        def inner(future):
            results, content_type = future.result()
            self._write_results_to_client(context, results, content_type)

            if should_store:
                self._store_results(context, results)

        self.context.thread_pool.queue(
            operation=functools.partial(self._load_results, context),
            callback=inner,
        )

    def _write_results_to_client(self, context, results, content_type):
        max_age = context.config.MAX_AGE

        if context.request.max_age is not None:
            max_age = context.request.max_age

        if context.request.prevent_result_storage or context.request.detection_error:
            max_age = context.config.MAX_AGE_TEMP_IMAGE

        if max_age:
            self.set_header('Cache-Control', 'max-age=' + str(max_age) + ',public')
            self.set_header('Expires', datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age))

        self.set_header('Server', 'Thumbor/%s' % __version__)
        self.set_header('Content-Type', content_type)

        if isinstance(results, ResultStorageResult):
            buffer = results.buffer
        else:
            buffer = results

        # auto-convert configured?
        should_vary = context.config.AUTO_WEBP
        # we have image (not video)
        should_vary = should_vary and content_type.startswith("image/")
        # output format is not requested via format filter
        should_vary = should_vary and not (
            context.request.format  # format is supported by filter
            and bool(re.search(r"format\([^)]+\)", context.request.filters))  # filter is in request
        )
        # our image is not animated gif
        should_vary = should_vary and not self.is_animated_gif(buffer)

        if should_vary:
            self.set_header('Vary', 'Accept')

        context.headers = self._headers.copy()

        self._response_ext = EXTENSION.get(content_type)
        self._response_length = len(buffer)

        self.write(buffer)
        self.finish()

    def _store_results(self, context, results):
        if not context.modules.result_storage or context.request.prevent_result_storage:
            return

        @gen.coroutine
        def save_to_result_storage():
            start = datetime.datetime.now()

            yield gen.maybe_future(context.modules.result_storage.put(results))

            finish = datetime.datetime.now()
            context.metrics.incr('result_storage.bytes_written', len(results))
            context.metrics.timing('result_storage.outgoing_time', (finish - start).total_seconds() * 1000)

        tornado.ioloop.IOLoop.instance().add_callback(save_to_result_storage)

    def optimize(self, context, image_extension, results):
        for optimizer in context.modules.optimizers:
            new_results = optimizer(context).run_optimizer(image_extension, results)
            if new_results is not None:
                results = new_results

        return results

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
        """

        :param url:
        :type url:
        :return:
        :rtype:
        """
        fetch_result = FetchResult()

        storage = self.context.modules.storage

        yield self.acquire_url_lock(url)

        try:
            fetch_result.buffer = yield gen.maybe_future(storage.get(url))
            mime = None

            if fetch_result.buffer is not None:
                self.release_url_lock(url)

                fetch_result.successful = True

                self.context.metrics.incr('storage.hit')
                mime = BaseEngine.get_mimetype(fetch_result.buffer)
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

        if isinstance(loader_result, LoaderResult):
            # TODO _fetch should probably return a result object vs a list to
            # to allow returning metadata
            if not loader_result.successful:
                fetch_result.buffer = None
                fetch_result.loader_error = loader_result.error
                raise gen.Return(fetch_result)

            fetch_result.buffer = loader_result.buffer
        else:
            # Handle old loaders
            fetch_result.buffer = loader_result

        if fetch_result.buffer is None:
            raise gen.Return(fetch_result)

        fetch_result.successful = True

        if mime is None:
            mime = BaseEngine.get_mimetype(fetch_result.buffer)

        self.context.request.extension = extension = EXTENSION.get(mime, '.jpg')

        original_preserve = self.context.config.PRESERVE_EXIF_INFO
        self.context.config.PRESERVE_EXIF_INFO = True

        try:
            if mime == 'image/gif' and self.context.config.USE_GIFSICLE_ENGINE:
                self.context.request.engine = self.context.modules.gif_engine
            else:
                self.context.request.engine = self.context.modules.engine

            self.context.request.engine.load(fetch_result.buffer, extension)

            if self.context.request.engine.image is None:
                fetch_result.successful = False
                fetch_result.buffer = None
                fetch_result.engine = self.context.request.engine
                fetch_result.engine_error = EngineResult.COULD_NOT_LOAD_IMAGE
                raise gen.Return(fetch_result)

            fetch_result.normalized = self.context.request.engine.normalize()

            # Allows engine or loader to override storage on the fly for the purpose of
            # marking a specific file as unstoreable
            storage = self.context.modules.storage

            is_no_storage = isinstance(storage, NoStorage)
            is_mixed_storage = isinstance(storage, MixedStorage)
            is_mixed_no_file_storage = is_mixed_storage and isinstance(storage.file_storage, NoStorage)

            if not (is_no_storage or is_mixed_no_file_storage):
                fetch_result.buffer = self.context.request.engine.read(extension)
                storage.put(url, fetch_result.buffer)

            storage.put_crypto(url)
        except Exception:
            fetch_result.successful = False
        finally:
            self.context.config.PRESERVE_EXIF_INFO = original_preserve
            if not fetch_result.successful:
                raise
            fetch_result.buffer = None
            fetch_result.engine = self.context.request.engine
            raise gen.Return(fetch_result)

    @gen.coroutine
    def get_blacklist_contents(self):
        filename = 'blacklist.txt'

        exists = yield gen.maybe_future(self.context.modules.storage.exists(filename))
        if exists:
            blacklist = yield gen.maybe_future(self.context.modules.storage.get(filename))
            raise tornado.gen.Return(blacklist)
        else:
            raise tornado.gen.Return("")

    @gen.coroutine
    def acquire_url_lock(self, url):
        if url not in BaseHandler.url_locks:
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
        self.context.metrics.initialize(self)

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
        storage.put(id, body)
