#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import datetime
import functools
import re
import sys
import traceback

import pytz
import tornado.web
from tornado.locks import Condition

import thumbor.filters
from thumbor import __version__
from thumbor.context import Context, RequestParameters
from thumbor.engines import BaseEngine, EngineResult
from thumbor.engines.json_engine import JSONEngine
from thumbor.loaders import LoaderResult
from thumbor.result_storages import ResultStorageResult
from thumbor.storages.mixed_storage import Storage as MixedStorage
from thumbor.storages.no_storage import Storage as NoStorage
from thumbor.transformer import Transformer
from thumbor.utils import CONTENT_TYPE, EXTENSION, logger

HTTP_DATE_FMT = "%a, %d %b %Y %H:%M:%S GMT"

# Handlers should not override __init__ pylint: disable=attribute-defined-outside-init,arguments-differ
# pylint: disable=broad-except,abstract-method,too-many-branches,too-many-return-statements,too-many-statements,too-many-lines


class FetchResult:  # Data Object pylint: disable=too-few-public-methods
    def __init__(  # pylint: disable=too-many-positional-arguments
        self,
        normalized=False,
        buffer=None,
        engine=None,
        successful=False,
        loader_error=None,
    ):
        self.normalized = normalized
        self.engine = engine
        self.buffer = buffer
        self.successful = successful
        self.loader_error = loader_error
        self.exception = None


class BaseHandler(tornado.web.RequestHandler):
    url_locks = {}

    def prepare(self):
        super().prepare()

        if not hasattr(self, "context"):
            return

        self._response_ext = None
        self._response_length = None

        self._response_start = datetime.datetime.now()
        self.context.metrics.incr("response.count")

    def on_finish(self):
        super().on_finish()
        self.context = getattr(self, "context", None)

        if self.context is None:
            return

        if not hasattr(self.context, "request"):
            self.context.request = RequestParameters()

        total_time = (
            datetime.datetime.now() - self._response_start
        ).total_seconds() * 1000
        status = self.get_status()
        self.context.metrics.timing("response.time", total_time)
        self.context.metrics.timing(f"response.time.{status}", total_time)
        self.context.metrics.incr(f"response.status.{status}")

        if status == 200 and self.context is not None:
            if self.context.request.smart:
                self.context.metrics.incr("response.smart.count")
                self.context.metrics.timing(
                    "response.smart.latency", total_time
                )
            else:
                self.context.metrics.incr("response.not_smart.count")
                self.context.metrics.timing(
                    "response.not_smart.latency", total_time
                )

        if self._response_ext is not None:
            ext = self._response_ext
            self.context.metrics.incr(f"response.format{ext}")
            self.context.metrics.timing(f"response.time{ext}", total_time)

            if self._response_length is not None:
                self.context.metrics.incr(
                    f"response.bytes{ext}", self._response_length
                )

    def _error(self, status, msg=None):
        self.set_status(status)

        if msg is not None:
            logger.warning(msg)
        self.finish()

    async def execute_image_operations(self):
        self.context.request.quality = None

        req = self.context.request
        conf = self.context.config

        total_time = (
            datetime.datetime.now() - self._response_start
        ).total_seconds() * 1000

        if self.context.request.smart:
            self.context.metrics.incr("response.smart.count")
            self.context.metrics.timing("response.smart.latency", total_time)
        else:
            self.context.metrics.incr("response.none_smart.count")
            self.context.metrics.timing(
                "response.none_smart.latency", total_time
            )

        should_store = (
            self.context.config.RESULT_STORAGE_STORES_UNSAFE
            or not self.context.request.unsafe
        )

        if self.context.modules.result_storage and should_store:
            start = datetime.datetime.now()

            try:
                result = await self.context.modules.result_storage.get()
            except Exception as error:
                logger.exception(
                    "[BaseHander.execute_image_operations] %s", error
                )
                self._error(
                    500,
                    "Error while trying to get the image "
                    f"from the result storage: {error}",
                )

                return

            finish = datetime.datetime.now()

            self.context.metrics.timing(
                "result_storage.incoming_time",
                (finish - start).total_seconds() * 1000,
            )

            if result is None:
                self.context.metrics.incr("result_storage.miss")
            else:
                self.context.metrics.incr("result_storage.hit")
                self.context.metrics.incr(
                    "result_storage.bytes_read", len(result)
                )
                logger.debug("[RESULT_STORAGE] IMAGE FOUND: %s", req.url)
                await self.finish_request(result)

                return

        if (
            conf.MAX_WIDTH
            and (not isinstance(req.width, str))
            and req.width > conf.MAX_WIDTH
        ):
            req.width = conf.MAX_WIDTH

        if (
            conf.MAX_HEIGHT
            and (not isinstance(req.height, str))
            and req.height > conf.MAX_HEIGHT
        ):
            req.height = conf.MAX_HEIGHT

        req.meta_callback = (
            conf.META_CALLBACK_NAME
            or self.request.arguments.get("callback", [None])[0]
        )

        self.filters_runner = self.context.filters_factory.create_instances(
            self.context, self.context.request.filters
        )
        # Apply all the filters from the PRE_LOAD phase
        # and call get_image() afterwards.
        await self.filters_runner.apply_filters(
            thumbor.filters.PHASE_PRE_LOAD,
        )
        await self.get_image()

    # TODO: refactor this
    async def get_image(self):
        """
        This function is called after the PRE_LOAD filters have been applied.
        It applies the AFTER_LOAD filters on the result, then crops the image.
        """
        try:
            result = await self._fetch(self.context.request.image_url)

            if not result.successful:
                if result.loader_error == LoaderResult.ERROR_NOT_FOUND:
                    self._error(404)

                    return

                if result.loader_error == LoaderResult.ERROR_UPSTREAM:
                    # Return a Bad Gateway status if the error
                    # came from upstream
                    self._error(502)

                    return

                if result.loader_error == LoaderResult.ERROR_TIMEOUT:
                    # Return a Gateway Timeout status if upstream
                    # timed out (i.e. 599)
                    self._error(504)

                    return

                if isinstance(result.loader_error, int):
                    self._error(result.loader_error)

                    return

                if (
                    hasattr(result, "engine_error")
                    and result.engine_error
                    == EngineResult.COULD_NOT_LOAD_IMAGE
                ):
                    self._error(400)

                    return

                self._error(500)

                return

        except Exception as error:
            req_url = self.context.request.image_url
            msg = f"[BaseHandler] get_image failed for url `{req_url}`. error: `{error}`"

            self.log_exception(*sys.exc_info())

            if "cannot identify image file" in str(error):
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
            except Exception as error:
                logger.exception("Loading image failed with %s", error)
                self._error(504)

                return

        if not normalized:
            normalized = engine.normalize()

        self.context.transformer = Transformer(self.context)

        await self.filters_runner.apply_filters(
            thumbor.filters.PHASE_AFTER_LOAD
        )
        self.normalize_crops(normalized, req, engine)

        if req.meta:
            self.context.transformer.engine = self.context.request.engine = (
                JSONEngine(engine, req.image_url, req.meta_callback)
            )

        await self.context.transformer.transform()
        await self.after_transform()

    def normalize_crops(self, normalized, req, engine):
        new_crops = None

        if normalized and req.should_crop:
            crop_left = req.crop["left"]
            crop_top = req.crop["top"]
            crop_right = req.crop["right"]
            crop_bottom = req.crop["bottom"]

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
                crop_bottom,
            )
            req.crop["left"] = new_crops[0]
            req.crop["top"] = new_crops[1]
            req.crop["right"] = new_crops[2]
            req.crop["bottom"] = new_crops[3]

    async def after_transform(self):
        if (
            self.context.request.extension != ".gif"
            or self.context.config.USE_GIFSICLE_ENGINE is None
        ):
            await self.filters_runner.apply_filters(
                thumbor.filters.PHASE_POST_TRANSFORM
            )

        await self.finish_request()

    def is_webp(self, context):
        return (
            context.config.AUTO_WEBP
            and context.request.accepts_webp
            and not context.request.engine.is_multiple()
            and context.request.engine.can_convert_to_webp()
        )

    def is_animated_gif(self, data):
        if data[:6] not in [b"GIF87a", b"GIF89a"]:
            return False
        i = 10  # skip header
        frames = 0

        def skip_color_table(i, flags):
            if flags & 0x80:
                i += 3 << ((flags & 7) + 1)

            return i

        flags = data[i]
        i = skip_color_table(i + 3, flags)

        while frames < 2:
            block = data[i : i + 1]  # NOQA
            i += 1

            if block == b"\x3b":
                break

            if block == b"\x21":
                i += 1
            elif block == b"\x2c":
                frames += 1
                i += 8
                i = skip_color_table(i + 1, data[i])
                i += 1
            else:
                return False

            while True:
                j = data[i]
                i += 1

                if not j:
                    break
                i += j

        return frames > 1

    def can_auto_convert_png_to_jpg(self):
        request_override = self.context.request.auto_png_to_jpg
        config = self.context.config

        enabled = (
            request_override is None
            if config.AUTO_PNG_TO_JPG
            else request_override
        )

        if enabled:
            return self.context.request.engine.can_auto_convert_png_to_jpg()

        return False

    def accepts_mime_type(self, mimetype=""):
        if self.context.request and self.context.request.headers:
            return mimetype in self.context.request.headers.get("Accept", "")

        return False

    def can_auto_convert_to_avif(self):
        auto_avif = self.context.config.AUTO_AVIF
        accepts_avif = self.accepts_mime_type("image/avif")

        if (
            auto_avif is True
            and accepts_avif is True
            and not self.context.request.engine.is_multiple()
        ):
            return self.context.request.engine.can_auto_convert_to_avif()

        return False

    def can_auto_convert_to_heif(self):
        auto_heif = self.context.config.AUTO_HEIF
        accepts_heif = self.accepts_mime_type("image/heif")

        if (
            auto_heif
            and accepts_heif
            and not self.context.request.engine.is_multiple()
        ):
            return self.context.request.engine.can_auto_convert_to_heif()

        return False

    def can_auto_convert_to_jpg(self):
        auto_jpg = self.context.config.AUTO_JPG
        accepts_jpg = (
            self.accepts_mime_type("*/*")
            or self.accepts_mime_type("image/jpg")
            or self.accepts_mime_type("image/jpeg")
        )

        if (
            auto_jpg
            and accepts_jpg
            and not self.context.request.engine.is_multiple()
            and not self.context.request.engine.has_transparency()
        ):
            return True

        return False

    def can_auto_convert_to_png(self):
        auto_png = self.context.config.AUTO_PNG
        accepts_png = self.accepts_mime_type("image/png")

        if (
            auto_png
            and accepts_png
            and not self.context.request.engine.is_multiple()
        ):
            return True

        return False

    def define_image_type(self, context, result):
        if result is not None:
            if isinstance(result, ResultStorageResult):
                buffer = result.buffer
            else:
                buffer = result
            image_extension = EXTENSION.get(
                BaseEngine.get_mimetype(buffer), ".jpg"
            )
            content_type = CONTENT_TYPE.get(
                image_extension, CONTENT_TYPE[".jpg"]
            )

            return image_extension, content_type

        image_extension = context.request.format

        if image_extension is not None:
            image_extension = f".{image_extension}"
            logger.debug("Image format specified as %s.", image_extension)
        elif self.is_webp(context):
            image_extension = ".webp"
            logger.debug(
                "Image format set by AUTO_WEBP as %s.", image_extension
            )
        elif self.can_auto_convert_to_avif():
            image_extension = ".avif"
            logger.debug(
                "Image format set by AUTO_AVIF as %s.", image_extension
            )
        elif (
            self.can_auto_convert_png_to_jpg()
            or self.can_auto_convert_to_jpg()
        ):
            image_extension = ".jpg"
            logger.debug(
                "Image format set by AUTO_PNG_TO_JPG or AUTO_JPG as %s.",
                image_extension,
            )
        elif self.can_auto_convert_to_heif():
            image_extension = ".heif"
            logger.debug(
                "Image format set by AUTO_HEIF as %s.", image_extension
            )
        elif self.can_auto_convert_to_png():
            image_extension = ".png"
            logger.debug(
                "Image format set by AUTO_PNG as %s.", image_extension
            )
        else:
            image_extension = context.request.engine.extension
            logger.debug(
                "No image format specified. Retrieving "
                "from the image extension: %s.",
                image_extension,
            )

        content_type = CONTENT_TYPE.get(image_extension, CONTENT_TYPE[".jpg"])

        if context.request.meta:
            context.request.meta_callback = (
                context.config.META_CALLBACK_NAME
                or self.request.arguments.get("callback", [None])[0]
            )
            content_type = (
                "text/javascript"
                if context.request.meta_callback
                else "application/json"
            )
            logger.debug(
                "Metadata requested. Serving content type of %s.", content_type
            )

        logger.debug("Content Type of %s detected.", content_type)

        return (image_extension, content_type)

    def _load_results(self, context):
        image_extension, content_type = self.define_image_type(context, None)

        quality = self.context.request.quality

        if quality is None:
            if (
                image_extension == ".webp"
                and self.context.config.WEBP_QUALITY is not None
            ):
                quality = self.context.config.get("WEBP_QUALITY")
            elif (
                image_extension == ".avif"
                and self.context.config.AVIF_QUALITY is not None
            ):
                quality = self.context.config.AVIF_QUALITY
            elif image_extension in (".heif", ".heic"):
                quality = self.context.config.HEIF_QUALITY
                if quality is None:
                    quality = 75
            else:
                quality = self.context.config.QUALITY

        results = context.request.engine.read(image_extension, quality)

        if context.request.max_bytes is not None:
            results = self.reload_to_fit_in_kb(
                context.request.engine,
                results,
                image_extension,
                quality,
                context.request.max_bytes,
            )

        if not context.request.meta:
            results = self.optimize(context, image_extension, results)
            # An optimizer might have modified the image format.
            content_type = BaseEngine.get_mimetype(results)

        return results, content_type

    async def _process_result_from_storage(self, result):
        if self.context.config.SEND_IF_MODIFIED_LAST_MODIFIED_HEADERS:
            # Handle If-Modified-Since & Last-Modified header
            try:
                if isinstance(result, ResultStorageResult):
                    result_last_modified = result.last_modified
                else:
                    result_last_modified = await (
                        self.context.modules.result_storage.last_updated()
                    )

                if result_last_modified:
                    if "If-Modified-Since" in self.request.headers:
                        date_modified_since = datetime.datetime.strptime(
                            self.request.headers["If-Modified-Since"],
                            HTTP_DATE_FMT,
                        ).replace(tzinfo=pytz.utc)

                        if result_last_modified <= date_modified_since:
                            self.set_status(304)
                            self.finish()

                            return

                    self.set_header(
                        "Last-Modified",
                        result_last_modified.strftime(HTTP_DATE_FMT),
                    )
            except NotImplementedError:
                logger.warning(
                    "last_updated method is not supported by your "
                    "result storage service, hence If-Modified-Since & "
                    "Last-Updated headers support is disabled."
                )

    async def finish_request(self, result_from_storage=None):
        if result_from_storage is not None:
            await self._process_result_from_storage(result_from_storage)

            _, content_type = self.define_image_type(
                self.context, result_from_storage
            )
            await self._write_results_to_client(
                result_from_storage, content_type
            )

            return

        context = self.context
        result_storage = context.modules.result_storage
        metrics = context.metrics

        should_store = (
            result_storage
            and not context.request.prevent_result_storage
            and (
                context.config.RESULT_STORAGE_STORES_UNSAFE
                or not context.request.unsafe
            )
        )

        try:
            result = await self.context.thread_pool.queue(
                operation=functools.partial(self._load_results, context),
            )
        except Exception as error:  # pylint: disable=broad-except
            logger.exception("[BaseHander.finish_request] %s", error)
            self._error(500, f"Error while trying to fetch the image: {error}")

            if self.context.config.USE_CUSTOM_ERROR_HANDLING:
                self.context.modules.importer.error_handler.handle_error(
                    context=self.context,
                    handler=self.context.request_handler,
                    exception=sys.exc_info(),
                )

            return

        (results, content_type) = result
        await self._write_results_to_client(results, content_type)

        if should_store:
            results = self._ensure_bytes(results)
            await self._store_results(result_storage, metrics, results)

        # can't cleanup before storing results as the storage requires context
        self._cleanup()

    def _ensure_bytes(self, results):
        if isinstance(results, str):
            return results.encode()
        return results

    def _cleanup(self):
        self.context.request_handler = None

        if hasattr(self.context, "request"):
            self.context.request.engine = None
        self.context.modules = None
        self.context.filters_factory = None
        self.context.metrics = None
        self.context.thread_pool = None
        self.context.transformer = None
        self.context = None  # Handlers should not override __init__ pylint: disable=attribute-defined-outside-init

    async def _write_results_to_client(self, results, content_type):
        max_age = self.context.config.MAX_AGE

        if self.context.request.max_age is not None:
            max_age = self.context.request.max_age

        if (
            self.context.request.prevent_result_storage
            or self.context.request.detection_error
        ):
            max_age = self.context.config.MAX_AGE_TEMP_IMAGE

        if max_age:
            self.set_header(
                "Cache-Control", "max-age=" + str(max_age) + ",public"
            )
            self.set_header(
                "Expires",
                datetime.datetime.utcnow()
                + datetime.timedelta(seconds=max_age),
            )

        if hasattr(self.context.config, "ACCESS_CONTROL_ALLOW_ORIGIN_HEADER"):
            ac_header = self.context.config.ACCESS_CONTROL_ALLOW_ORIGIN_HEADER

            if ac_header is not False:
                self.set_header("Access-Control-Allow-Origin", ac_header)
                logger.debug("CORS header found. Set to: %s", ac_header)

        self.set_header("Server", f"Thumbor/{__version__}")
        self.set_header("Content-Type", content_type)

        if isinstance(results, ResultStorageResult):
            buffer = results.buffer
        else:
            buffer = results

        # auto-convert configured?
        should_vary = (
            self.context.config.AUTO_WEBP
            or self.context.config.AUTO_AVIF
            or self.context.config.AUTO_HEIF
        )
        # we have image (not video)
        should_vary = should_vary and content_type.startswith("image/")
        # output format is not requested via format filter
        should_vary = should_vary and not (
            self.context.request.format
            and bool(  # format is supported by filter
                re.search(r"format\([^)]+\)", self.context.request.filters)
            )  # filter is in request
        )
        # our image is not animated gif
        should_vary = should_vary and not self.is_animated_gif(buffer)

        if should_vary:
            self.set_header("Vary", "Accept")

        self.context.headers = self._headers.copy()
        self._response_ext = EXTENSION.get(content_type)
        self._response_length = len(buffer)

        self.write(buffer)
        self.finish()

    async def _store_results(self, result_storage, metrics, results):
        start = datetime.datetime.now()

        await result_storage.put(results)

        finish = datetime.datetime.now()
        metrics.incr("result_storage.bytes_written", len(results))
        metrics.timing(
            "result_storage.outgoing_time",
            (finish - start).total_seconds() * 1000,
        )

    def optimize(self, context, image_extension, results):
        for optimizer in context.modules.optimizers:
            new_results = optimizer(context).run_optimizer(
                image_extension, results
            )

            if new_results is not None:
                results = new_results

        return results

    @staticmethod
    def reload_to_fit_in_kb(
        engine, initial_results, extension, initial_quality, max_bytes
    ):
        if (
            extension not in [".webp", ".jpg", ".jpeg"]
            or len(initial_results) <= max_bytes
        ):
            return initial_results

        results = initial_results
        quality = initial_quality

        while len(results) > max_bytes:
            quality = int(quality * 0.75)

            if quality < 10:
                logger.debug(
                    "Could not find any reduction that matches "
                    "required size of %d bytes.",
                    max_bytes,
                )

                return initial_results

            logger.debug(
                "Trying to downsize image with quality of %d...", quality
            )
            results = engine.read(extension, quality)

        prev_result = results

        while len(results) <= max_bytes and quality < initial_quality:
            quality = max(initial_quality, int(quality * 1.1))
            logger.debug(
                "Trying to upsize image with quality of %d...", quality
            )
            prev_result = results
            results = engine.read(extension, quality)

        return prev_result

    @classmethod
    def translate_crop_coordinates(  # pylint: disable=too-many-positional-arguments
        cls,
        original_width,
        original_height,
        width,
        height,
        crop_left,
        crop_top,
        crop_right,
        crop_bottom,
    ):
        if original_width == width and original_height == height:
            return None

        crop_left = crop_left * width // original_width
        crop_top = crop_top * height // original_height

        crop_right = crop_right * width // original_width
        crop_bottom = crop_bottom * height // original_height

        return (crop_left, crop_top, crop_right, crop_bottom)

    def validate(self, path):
        if not hasattr(self.context.modules.loader, "validate"):
            return True

        is_valid = self.context.modules.loader.validate(self.context, path)

        if not is_valid:
            logger.warning(
                (
                    'Request denied because the specified path "%s" was '
                    "not identified by the loader as a valid path"
                ),
                path,
            )

        return is_valid

    async def _fetch(self, url):
        """

        :param url:
        :type url:
        :return:
        :rtype:
        """
        fetch_result = FetchResult()

        storage = self.context.modules.storage

        await self.acquire_url_lock(url)

        try:
            fetch_result.buffer = await storage.get(url)
            mime = None

            if fetch_result.buffer is not None:
                self.release_url_lock(url)

                fetch_result.successful = True

                self.context.metrics.incr("storage.hit")

                mime = BaseEngine.get_mimetype(fetch_result.buffer)
                self.context.request.extension = EXTENSION.get(mime, ".jpg")

                if (
                    mime == "image/gif"
                    and self.context.config.USE_GIFSICLE_ENGINE
                ):
                    self.context.request.engine = (
                        self.context.modules.gif_engine
                    )
                else:
                    self.context.request.engine = self.context.modules.engine

                return fetch_result

            self.context.metrics.incr("storage.miss")

            loader_result = await self.context.modules.loader.load(
                self.context, url
            )
        finally:
            self.release_url_lock(url)

        if isinstance(loader_result, LoaderResult):
            # TODO _fetch should probably return a result object vs a list to
            # to allow returning metadata

            if not loader_result.successful:
                fetch_result.buffer = None
                fetch_result.loader_error = loader_result.error

                return fetch_result

            fetch_result.buffer = loader_result.buffer
        else:
            # Handle old loaders
            fetch_result.buffer = loader_result

        if fetch_result.buffer is None:
            return fetch_result

        fetch_result.successful = True

        if mime is None:
            mime = BaseEngine.get_mimetype(fetch_result.buffer)

        self.context.request.extension = extension = EXTENSION.get(
            mime, ".jpg"
        )

        try:
            if mime == "image/gif" and self.context.config.USE_GIFSICLE_ENGINE:
                self.context.request.engine = self.context.modules.gif_engine
            else:
                self.context.request.engine = self.context.modules.engine

            self.context.request.engine.load(fetch_result.buffer, extension)

            if self.context.request.engine.image is None:
                fetch_result.successful = False
                fetch_result.buffer = None
                fetch_result.engine = self.context.request.engine
                fetch_result.engine_error = EngineResult.COULD_NOT_LOAD_IMAGE

                return fetch_result

            fetch_result.normalized = self.context.request.engine.normalize()

            # Allows engine or loader to override storage
            # on the fly for the purpose of
            # marking a specific file as unstoreable
            storage = self.context.modules.storage

            is_no_storage = isinstance(storage, NoStorage)
            is_mixed_storage = isinstance(storage, MixedStorage)
            is_mixed_no_file_storage = is_mixed_storage and isinstance(
                storage.file_storage, NoStorage
            )

            if not (is_no_storage or is_mixed_no_file_storage):
                await storage.put(url, fetch_result.buffer)

            await storage.put_crypto(url)
        except Exception as error:
            fetch_result.successful = False
            fetch_result.exception = error

        if not fetch_result.successful and fetch_result.exception is not None:
            raise fetch_result.exception
        fetch_result.buffer = None
        fetch_result.engine = self.context.request.engine

        return fetch_result

    async def get_blacklist_contents(self):
        filename = "blacklist.txt"

        exists = await self.context.modules.storage.exists(filename)

        if exists:
            blacklist = await self.context.modules.storage.get(filename)

            return blacklist.decode()

        return ""

    async def acquire_url_lock(self, url):
        if url not in BaseHandler.url_locks:
            BaseHandler.url_locks[url] = Condition()
        else:
            return await BaseHandler.url_locks[url].wait()

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
            request_handler=self,
        )
        self.context.metrics.initialize(self)

    def log_exception(self, *exc_info):
        if isinstance(exc_info[1], tornado.web.HTTPError):
            # Delegate HTTPError's to the base class
            # We don't want these through normal exception handling
            super().log_exception(*exc_info)

            return

        msg = traceback.format_exception(  # pylint: disable=no-value-for-parameter
            *exc_info
        )

        try:
            if self.context.config.USE_CUSTOM_ERROR_HANDLING:
                self.context.modules.importer.error_handler.handle_error(
                    context=self.context, handler=self, exception=exc_info
                )
        finally:
            del exc_info
            logger.error("ERROR: %s", "".join(msg))


##
# Base handler for Image API operations
##
class ImageApiHandler(ContextHandler):
    def validate(self, body):  # pylint: disable=arguments-renamed
        conf = self.context.config
        mime = BaseEngine.get_mimetype(body)

        if mime == "image/gif" and self.context.config.USE_GIFSICLE_ENGINE:
            engine = self.context.modules.gif_engine
        else:
            engine = self.context.modules.engine

        # Check if image is valid
        try:
            engine.load(body, None)
        except IOError:
            self._error(415, "Unsupported Media Type")

            return False

        # Check weight constraints

        if (
            conf.UPLOAD_MAX_SIZE != 0
            and len(self.request.body) > conf.UPLOAD_MAX_SIZE
        ):
            self._error(
                412,
                "Image exceed max weight "
                f"(Expected : {conf.UPLOAD_MAX_SIZE}, Actual : {len(self.request.body)})",
            )

            return False

        # Check size constraints
        size = engine.size

        if conf.MIN_WIDTH > size[0] or conf.MIN_HEIGHT > size[1]:
            self._error(
                412,
                "Image is too small (Expected: %s/%s , Actual : %s/%s) % "
                "(conf.MIN_WIDTH, conf.MIN_HEIGHT, size[0], size[1])",
            )

            return False

        return True

    async def write_file(self, file_id, body):
        storage = self.context.modules.upload_photo_storage
        await storage.put(file_id, body)
