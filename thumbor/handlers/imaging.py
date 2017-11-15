#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com
import datetime
import re
import sys
import functools
import pytz
import tornado.gen as gen
import tornado.web
from six.moves.urllib.parse import quote, unquote
from tornado.locks import Condition

import thumbor.filters
from thumbor import __version__
from thumbor.context import RequestParameters
from thumbor.engines import BaseEngine, EngineResult
from thumbor.engines.json_engine import JSONEngine
from thumbor.handlers import ContextHandler
from thumbor.loaders import LoaderResult
from thumbor.result_storages import ResultStorageResult
from thumbor.storages.mixed_storage import Storage as MixedStorage
from thumbor.storages.no_storage import Storage as NoStorage
from thumbor.transformer import Transformer
from thumbor.utils import logger, CONTENT_TYPE, EXTENSION

try:
    basestring  # Python 2
except NameError:
    basestring = str  # Python 3

HTTP_DATE_FMT = "%a, %d %b %Y %H:%M:%S GMT"


class FetchResult(object):
    def __init__(self, normalized=False, buffer=None, engine=None, successful=False, loader_error=None):
        self.normalized = normalized
        self.engine = engine
        self.buffer = buffer
        self.successful = successful
        self.loader_error = loader_error


class ImagingHandler(ContextHandler):
    url_locks = {}

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

        return crop_left, crop_top, crop_right, crop_bottom

    def compute_etag(self):
        if self.context.config.ENABLE_ETAGS:
            return super(ImagingHandler, self).compute_etag()
        else:
            return None

    @gen.coroutine  # NOQA
    def check_image(self, kw):
        if self.context.config.MAX_ID_LENGTH > 0:
            # Check if an image with an uuid exists in storage
            image_key = kw['image'][:self.context.config.MAX_ID_LENGTH]
            exists = yield gen.maybe_future(self.context.modules.storage.exists(image_key))
            if exists:
                kw['image'] = image_key

        url = self.request.path

        kw['image'] = quote(kw['image'].encode('utf-8'))
        if not self.validate(kw['image']):
            raise tornado.web.HTTPError(400, 'No original image was specified in the given URL')

        kw['request'] = self.request
        self.context.request = RequestParameters(**kw)

        has_none = not self.context.request.unsafe and not self.context.request.hash
        has_both = self.context.request.unsafe and self.context.request.hash

        if has_none or has_both:
            raise tornado.web.HTTPError(400, 'URL does not have hash or unsafe, or has both: %s' % url)

        if self.context.request.unsafe and not self.context.config.ALLOW_UNSAFE_URL:
            raise tornado.web.HTTPError(400, 'URL has unsafe but unsafe is not allowed by the config: %s' % url)

        if self.context.config.USE_BLACKLIST:
            blacklist = yield self.get_blacklist_contents()
            if self.context.request.image_url in blacklist:
                raise tornado.web.HTTPError(
                    400,
                    'Source image url has been blacklisted: %s' % self.context.request.image_url
                )

        url_signature = self.context.request.hash
        if url_signature:
            signer = self.context.modules.url_signer(self.context.server.security_key)

            try:
                quoted_hash = quote(self.context.request.hash)
            except KeyError:
                raise tornado.web.HTTPError(400, 'Invalid hash: %s' % self.context.request.hash)

            url_to_validate = url.replace('/%s/' % self.context.request.hash, '') \
                .replace('/%s/' % quoted_hash, '')

            valid = signer.validate(unquote(url_signature), url_to_validate)

            if not valid and self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
                # Retrieves security key for this image if it has been seen before
                security_key = yield gen.maybe_future(
                    self.context.modules.storage.get_crypto(self.context.request.image_url))
                if security_key is not None:
                    signer = self.context.modules.url_signer(security_key)
                    valid = signer.validate(url_signature, url_to_validate)

            if not valid:
                raise tornado.web.HTTPError(500, 'Malformed URL')

        yield self.execute_image_operations()

    def validate(self, path):
        if not hasattr(self.context.modules.loader, 'validate'):
            return True

        is_valid = self.context.modules.loader.validate(self.context, path)

        if not is_valid:
            logger.warn('Request denied because the specified path "%s" was not identified by the loader as a valid '
                        'path' % path)

        return is_valid

    @gen.coroutine
    def execute_image_operations(self):
        self.context.request.quality = None

        req = self.context.request
        conf = self.context.config

        should_store = conf.RESULT_STORAGE_STORES_UNSAFE or not req.unsafe
        if self.context.modules.result_storage and should_store:
            start = datetime.datetime.now()

            try:
                result = yield gen.maybe_future(self.context.modules.result_storage.get())
            except Exception as e:
                logger.exception('[BaseHander.execute_image_operations] %s', e)
                raise tornado.web.HTTPError(500,
                                            'Error while trying to get the image from the result storage: {}'.format(e))

            finish = datetime.datetime.now()

            self.context.metrics.timing('result_storage.incoming_time', (finish - start).total_seconds() * 1000)

            if result is None:
                self.context.metrics.incr('result_storage.miss')
            else:
                self.context.metrics.incr('result_storage.hit')
                self.context.metrics.incr('result_storage.bytes_read', len(result))
                logger.debug('[RESULT_STORAGE] IMAGE FOUND: %s' % req.url)
                yield self.finish_request_from_storage(result)
                return

        if conf.MAX_WIDTH and (not isinstance(req.width, basestring)) and req.width > conf.MAX_WIDTH:
            req.width = conf.MAX_WIDTH
        if conf.MAX_HEIGHT and (not isinstance(req.height, basestring)) and req.height > conf.MAX_HEIGHT:
            req.height = conf.MAX_HEIGHT

        req.meta_callback = conf.META_CALLBACK_NAME or self.request.arguments.get('callback', [None])[0]

        self.filters_runner = self.context.filters_factory.create_instances(self.context, self.context.request.filters)
        # Apply all the filters from the PRE_LOAD phase and call get_image() afterwards.
        yield self.filters_runner.apply_filters(thumbor.filters.PHASE_PRE_LOAD)
        yield self.get_image()

    @gen.coroutine
    def finish_request_from_storage(self, result_from_storage):
        yield self._process_result_from_storage(result_from_storage)

        image_extension, content_type = self.define_image_type(result_from_storage)
        self._write_results_to_client(result_from_storage, content_type)

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
                logger.warn('last_updated method is not supported by your result storage service, '
                            'hence If-Modified-Since & '
                            'Last-Updated headers support is disabled.')

    def _write_results_to_client(self, results, content_type):
        max_age = self.context.config.MAX_AGE

        if self.context.request.max_age is not None:
            max_age = self.context.request.max_age

        if self.context.request.prevent_result_storage or self.context.request.detection_error:
            max_age = self.context.config.MAX_AGE_TEMP_IMAGE

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
        should_vary = self.context.config.AUTO_WEBP
        # we have image (not video)
        should_vary = should_vary and content_type.startswith("image/")
        # output format is not requested via format filter
        should_vary = should_vary and not (
            self.context.request.format and  # format is supported by filter
            bool(re.search(r"format\([^)]+\)", self.context.request.filters))  # filter is in request
        )
        # our image is not animated gif
        should_vary = should_vary and not self.is_animated_gif(buffer)

        if should_vary:
            self.set_header('Vary', 'Accept')

        self._response_ext = EXTENSION.get(content_type)
        self._response_length = len(buffer)

        self.write(buffer)
        self.finish()

    @staticmethod
    def is_animated_gif(data):
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
                skip = ord(data[i])
                i += 1
                if not skip:
                    break
                i += skip
        return frames > 1

    def can_auto_convert_png_to_jpg(self):
        return self.context.request.engine.can_auto_convert_png_to_jpg()

    def define_image_type(self, result=None):
        if result is not None:
            if isinstance(result, ResultStorageResult):
                buffer = result.buffer
            else:
                buffer = result
            image_extension = EXTENSION.get(BaseEngine.get_mimetype(buffer), '.jpg')
        else:
            image_extension = self.context.request.format
            if image_extension is not None:
                image_extension = '.%s' % image_extension
                logger.debug('Image format specified as %s.' % image_extension)
            elif self.is_webp():
                image_extension = '.webp'
                logger.debug('Image format set by AUTO_WEBP as %s.' % image_extension)
            elif self.can_auto_convert_png_to_jpg():
                image_extension = '.jpg'
                logger.debug('Image format set by AUTO_PNG_TO_JPG as %s.' % image_extension)
            else:
                image_extension = self.context.request.engine.extension
                logger.debug('No image format specified. Retrieving from the image extension: %s.' % image_extension)

        content_type = CONTENT_TYPE.get(image_extension, CONTENT_TYPE['.jpg'])

        if self.context.request.meta:
            self.context.request.meta_callback = self.context.config.META_CALLBACK_NAME or \
                self.request.arguments.get('callback', [None])[0]
            content_type = 'text/javascript' if self.context.request.meta_callback else 'application/json'
            logger.debug('Metadata requested. Serving content type of %s.' % content_type)

        logger.debug('Content Type of %s detected.' % content_type)

        return image_extension, content_type

    def is_webp(self):
        return (self.context.config.AUTO_WEBP and
                self.context.request.accepts_webp and
                not self.context.request.engine.is_multiple() and
                self.context.request.engine.can_convert_to_webp())

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
        except Exception as e:
            msg = '[BaseHandler] get_image failed for url `{url}`. error: `{error}`'.format(
                url=self.context.request.image_url,
                error=e
            )

            self.log_exception(*sys.exc_info())

            if 'cannot identify image file' in e.message:
                logger.warning(msg)
                raise tornado.web.HTTPError(400)
            else:
                logger.error(msg)
                raise tornado.web.HTTPError(500)

        if not result.successful:
            if result.loader_error == LoaderResult.ERROR_NOT_FOUND:
                raise tornado.web.HTTPError(404)
            elif result.loader_error == LoaderResult.ERROR_UPSTREAM:
                # Return a Bad Gateway status if the error came from upstream
                raise tornado.web.HTTPError(502)
            elif result.loader_error == LoaderResult.ERROR_TIMEOUT:
                # Return a Gateway Timeout status if upstream timed out (i.e. 599)
                raise tornado.web.HTTPError(504)
            elif isinstance(result.loader_error, int):
                raise tornado.web.HTTPError(result.loader_error)
            elif hasattr(result, 'engine_error') and result.engine_error == EngineResult.COULD_NOT_LOAD_IMAGE:
                raise tornado.web.HTTPError(400)
            else:
                raise tornado.web.HTTPError(500)

        normalized = result.normalized
        buffer = result.buffer
        engine = result.engine

        req = self.context.request

        if engine is None:
            if buffer is None:
                raise tornado.web.HTTPError(504)

            engine = self.context.request.engine
            try:
                engine.load(buffer, self.context.request.extension)
            except Exception:
                raise tornado.web.HTTPError(504)

        self.context.transformer = Transformer(self.context)

        yield self.filters_runner.apply_filters(thumbor.filters.PHASE_AFTER_LOAD)

        self.normalize_crops(normalized, req, engine)

        if req.meta:
            self.context.transformer.engine = \
                self.context.request.engine = \
                JSONEngine(engine, req.image_url, req.meta_callback)

        yield self.context.transformer.transform()
        yield self.after_transform()

    def normalize_crops(self, normalized, req, engine):
        if normalized and req.should_crop:
            crop_left = req.crop['left']
            crop_top = req.crop['top']
            crop_right = req.crop['right']
            crop_bottom = req.crop['bottom']

            actual_width, actual_height = engine.size

            if req.width:
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

    @gen.coroutine
    def after_transform(self):
        if self.context.request.extension != '.gif' or not self.context.config.USE_GIFSICLE_ENGINE:
            yield self.filters_runner.apply_filters(thumbor.filters.PHASE_POST_TRANSFORM)

        yield self.finish_request()

    @gen.coroutine
    def finish_request(self):
        should_store = self.context.modules.result_storage and not self.context.request.prevent_result_storage and (
            self.context.config.RESULT_STORAGE_STORES_UNSAFE or not self.context.request.unsafe)

        try:
            results, content_type = yield self._load_results()
        except Exception as e:
            logger.exception('[BaseHander.finish_request] %s', e)
            raise tornado.web.HTTPError(504, 'Error while trying to fetch the image: {}'.format(e))

        result_storage = self.context.modules.result_storage
        metrics = self.context.metrics
        self._write_results_to_client(results, content_type)

        if should_store:
            self._store_results(result_storage, metrics, results)

    @gen.coroutine
    def _load_results(self):
        image_extension, content_type = self.define_image_type()

        quality = self.context.request.quality
        if quality is None:
            if image_extension == '.webp' and self.context.config.WEBP_QUALITY is not None:
                quality = self.context.config.get('WEBP_QUALITY')
            else:
                quality = self.context.config.QUALITY

        results = yield self.context.thread_pool.queue(
            functools.partial(self.context.request.engine.read, image_extension, quality)
        )

        if self.context.request.max_bytes is not None:
            results = yield self.reload_to_fit_in_kb(
                self.context.request.engine,
                results,
                image_extension,
                quality,
                self.context.request.max_bytes
            )
        if not self.context.request.meta:
            results = yield self.optimize(image_extension, results)
            # An optimizer might have modified the image format.
            content_type = BaseEngine.get_mimetype(results)

        raise gen.Return((results, content_type))

    @gen.coroutine
    def optimize(self, image_extension, results):
        for optimizer_cls in self.context.modules.optimizers:
            optimizer = optimizer_cls(self.context)
            if (optimizer.should_run(image_extension, results)):
                new_results = yield self.context.thread_pool.queue(
                    functools.partial(optimizer.run_optimizer, image_extension, results)
                )
                if new_results is not None:
                    results = new_results

        raise gen.Return(results)

    @gen.coroutine
    def reload_to_fit_in_kb(self, engine, initial_results, extension, initial_quality, max_bytes):
        if extension not in ['.webp', '.jpg', '.jpeg'] or len(initial_results) <= max_bytes:
            raise gen.Return(initial_results)

        results = initial_results
        quality = initial_quality

        while len(results) > max_bytes:
            quality = int(quality * 0.75)

            if quality < 10:
                logger.debug('Could not find any reduction that matches required size of %d bytes.' % max_bytes)
                raise gen.Return(initial_results)

            logger.debug('Trying to downsize image with quality of %d...' % quality)
            results = yield self.context.thread_pool.queue(
                functools.partial(engine.read, extension, quality)
            )

        prev_result = results
        while len(results) <= max_bytes:
            quality = int(quality * 1.1)
            logger.debug('Trying to upsize image with quality of %d...' % quality)
            prev_result = results
            results = yield self.context.thread_pool.queue(
                functools.partial(engine.read, extension, quality)
            )

        raise gen.Return(prev_result)

    @gen.coroutine
    def _store_results(self, result_storage, metrics, results):
        start = datetime.datetime.now()

        yield gen.maybe_future(result_storage.put(results))

        finish = datetime.datetime.now()
        metrics.incr('result_storage.bytes_written', len(results))
        metrics.timing('result_storage.outgoing_time', (finish - start).total_seconds() * 1000)

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

        try:
            if mime == 'image/gif' and self.context.config.USE_GIFSICLE_ENGINE:
                self.context.request.engine = self.context.modules.gif_engine
            else:
                self.context.request.engine = self.context.modules.engine

            try:
                self.context.request.engine.load(fetch_result.buffer, extension)
            except Exception:
                pass

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
                storage.put(url, fetch_result.buffer)

            storage.put_crypto(url)
        except Exception:
            raise

        fetch_result.buffer = None
        fetch_result.engine = self.context.request.engine
        raise gen.Return(fetch_result)

    @gen.coroutine
    def acquire_url_lock(self, url):
        if url not in ImagingHandler.url_locks:
            ImagingHandler.url_locks[url] = Condition()
        else:
            yield ImagingHandler.url_locks[url].wait()

    def release_url_lock(self, url):
        try:
            ImagingHandler.url_locks[url].notify_all()
            del ImagingHandler.url_locks[url]
        except KeyError:
            pass

    @gen.coroutine
    def get(self, **kw):
        yield self.check_image(kw)

    @gen.coroutine
    def head(self, **kw):
        yield self.check_image(kw)
