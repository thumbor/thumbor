#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timedelta
from json import loads
from os.path import abspath, dirname, join
from shutil import which
from urllib.parse import quote

import pytest
import pytz
import tornado.web
from libthumbor import CryptoURL
from mock import Mock, patch
from preggy import expect
from tornado.testing import gen_test

from tests.base import TestCase, normalize_unicode_path
from tests.fixtures.images import (
    alabama1,
    animated_image,
    default_image,
    invalid_quantization,
    not_so_animated_image,
    space_image,
)
from thumbor.config import Config
from thumbor.context import Context, RequestParameters, ServerParameters
from thumbor.engines.pil import Engine
from thumbor.handlers import BaseHandler, FetchResult
from thumbor.importer import Importer
from thumbor.loaders import LoaderResult
from thumbor.result_storages.file_storage import Storage as FileResultStorage
from thumbor.server import validate_config
from thumbor.storages.file_storage import Storage as FileStorage
from thumbor.storages.no_storage import Storage as NoStorage

# pylint: disable=broad-except,abstract-method,attribute-defined-outside-init,line-too-long,too-many-public-methods
# pylint: disable=too-many-lines

JPEGTRAN_AVAILABLE = which("jpegtran") is not None
EXIFTOOL_AVAILABLE = which("exiftool") is not None


class FetchResultTestCase(TestCase):
    def test_can_create_default_fetch_result(self):
        result = FetchResult()
        expect(result.normalized).to_be_false()
        expect(result.buffer).to_be_null()
        expect(result.engine).to_be_null()
        expect(result.successful).to_be_false()
        expect(result.loader_error).to_be_null()

    def test_can_create_fetch_result(self):
        buffer_mock = Mock()
        engine_mock = Mock()
        error_mock = Mock()
        result = FetchResult(
            normalized=True,
            buffer=buffer_mock,
            engine=engine_mock,
            successful=True,
            loader_error=error_mock,
        )
        expect(result.normalized).to_be_true()
        expect(result.buffer).to_equal(buffer_mock)
        expect(result.engine).to_equal(engine_mock)
        expect(result.successful).to_be_true()
        expect(result.loader_error).to_equal(error_mock)


class ErrorHandler(BaseHandler):
    def get(self):
        self._error(403)


class BaseHandlerTestApp(tornado.web.Application):
    def __init__(self, context):
        self.context = context
        super(BaseHandlerTestApp, self).__init__([(r"/error", ErrorHandler)])


class BaseImagingTestCase(TestCase):
    def setUp(self):
        self.root_path = tempfile.mkdtemp()
        self.loader_path = abspath(join(dirname(__file__), "../fixtures/images/"))
        self.base_uri = "/image"
        super(BaseImagingTestCase, self). setUp()

    def tearDown(self):
        shutil.rmtree(self.root_path)


class ImagingOperationsWithHttpLoaderTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.http_loader"
        cfg.STORAGE = "thumbor.storages.file_storage"
        cfg.FILE_STORAGE_ROOT_PATH = self.root_path

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, "localhost", "thumbor.conf", None, "info", None)
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    @gen_test
    async def test_image_already_generated_by_thumbor(self):
        with open("./tests/fixtures/images/image.jpg", "rb") as fixture:
            await self.context.modules.storage.put(
                quote("http://test.com/smart/image.jpg"), fixture.read()
            )
        crypto = CryptoURL("ACME-SEC")
        image_url = self.get_url(
            crypto.generate(image_url=quote("http://test.com/smart/image.jpg"))
        )
        url = crypto.generate(image_url=quote(image_url))

        response = await self.async_fetch(url)
        expect(response.code).to_equal(200)

    @gen_test
    async def test_image_already_generated_by_thumbor_2_times(self):
        with open(
            normalize_unicode_path(u"./tests/fixtures/images/alabama1_ap620é.jpg"),
            "rb",
        ) as fixture:
            await self.context.modules.storage.put(
                quote("http://test.com/smart/alabama1_ap620é"), fixture.read()
            )
        crypto = CryptoURL("ACME-SEC")
        image_url = self.get_url(
            crypto.generate(
                image_url=quote(
                    self.get_url(
                        crypto.generate(
                            image_url=quote("http://test.com/smart/alabama1_ap620é")
                        )
                    )
                )
            )
        )

        url = crypto.generate(image_url=quote(image_url))

        response = await self.async_fetch(url)
        expect(response.code).to_equal(200)

    @gen_test
    async def test_image_with_utf8_url(self):
        with open("./tests/fixtures/images/maracujá.jpg", "rb") as fixture:
            await self.context.modules.storage.put(
                quote(u"http://test.com/maracujá.jpg".encode("utf-8")), fixture.read(),
            )
        crypto = CryptoURL("ACME-SEC")
        image_url = self.get_url(
            quote(u"/unsafe/http://test.com/maracujá.jpg".encode("utf-8"))
        )
        url = crypto.generate(image_url=quote(image_url))
        response = await self.async_fetch(url)
        expect(response.code).to_equal(200)

    @gen_test
    async def test_image_with_http_utf8_url(self):
        with open("./tests/fixtures/images/maracujá.jpg", "rb") as fixture:
            await self.context.modules.storage.put(
                quote(u"http://test.com/maracujá.jpg".encode("utf-8")), fixture.read(),
            )

        url = quote(u"/unsafe/http://test.com/maracujá.jpg".encode("utf-8"))
        response = await self.async_fetch(url)
        expect(response.code).to_equal(200)


class ImagingOperationsTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.file_storage"
        cfg.FILE_STORAGE_ROOT_PATH = self.root_path
        cfg.QUALITY = "keep"
        cfg.SVG_DPI = 200

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, "localhost", "thumbor.conf", None, "info", None)
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    @gen_test
    async def test_can_get_image(self):
        response = await self.async_fetch("/unsafe/smart/image.jpg")
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(default_image())

    @gen_test
    async def test_can_get_image_without_extension(self):
        response = await self.async_fetch("/unsafe/smart/image")
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(default_image())

    @gen_test
    async def test_get_unknown_image_returns_not_found(self):
        response = await self.async_fetch("/unsafe/smart/imag")
        expect(response.code).to_equal(404)

    @gen_test
    async def test_can_get_unicode_image(self):
        response = await self.async_fetch(
            u"/unsafe/%s"
            % quote(u"15967251_212831_19242645_АгатавЗоопарке.jpg".encode("utf-8"))
        )
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(default_image())

    @gen_test
    async def test_can_get_signed_regular_image(self):
        response = await self.async_fetch(
            "/_wIUeSaeHw8dricKG2MGhqu5thk=/smart/image.jpg"
        )
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(default_image())

    @gen_test
    async def test_url_without_unsafe_or_hash_fails(self):
        response = await self.async_fetch("/alabama1_ap620%C3%A9.jpg")
        expect(response.code).to_equal(400)

    @gen_test
    async def test_url_without_image(self):
        response = await self.async_fetch("/unsafe/")
        expect(response.code).to_equal(400)

    @gen_test
    async def test_utf8_encoded_image_name_with_encoded_url(self):
        url = "/lc6e3kkm_2Ww7NWho8HPOe-sqLU=/smart/alabama1_ap620%C3%A9.jpg"
        response = await self.async_fetch(url)
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(alabama1())

    @gen_test
    async def test_url_with_encoded_hash(self):
        url = "/%D1%80=/alabama1_ap620%C3%A9.jpg"
        response = await self.async_fetch(url)
        expect(response.code).to_equal(400)

    @gen_test
    async def test_image_with_spaces_on_url(self):
        response = await self.async_fetch(u"/unsafe/image%20space.jpg")
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(space_image())

    @gen_test
    async def test_can_get_image_with_filter(self):
        response = await self.async_fetch(
            "/5YRxzS2yxZxj9SZ50SoZ11eIdDI=/filters:fill(blue)/image.jpg"
        )
        expect(response.code).to_equal(200)

    @gen_test
    async def test_can_get_image_with_invalid_quantization_table(self):
        response = await self.async_fetch("/unsafe/invalid_quantization.jpg")
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(invalid_quantization())

    @gen_test
    async def test_getting_invalid_image_returns_bad_request(self):
        response = await self.async_fetch("/unsafe/image_invalid.jpg")
        expect(response.code).to_equal(400)

    @gen_test
    async def test_getting_invalid_watermark_returns_bad_request(self):
        response = await self.async_fetch(
            "/unsafe/filters:watermark(boom.jpg,0,0,0)/image.jpg"
        )
        expect(response.code).to_equal(400)

    @gen_test
    async def test_can_read_monochromatic_jpeg(self):
        response = await self.async_fetch("/unsafe/grayscale.jpg")
        expect(response.code).to_equal(200)
        expect(response.body).to_be_jpeg()

    @gen_test
    async def test_can_read_image_with_small_width_and_no_height(self):
        response = await self.async_fetch("/unsafe/0x0:1681x596/1x/image.jpg")
        expect(response.code).to_equal(200)
        expect(response.body).to_be_jpeg()

    @gen_test
    async def test_can_read_cmyk_jpeg(self):
        response = await self.async_fetch("/unsafe/cmyk.jpg")
        expect(response.code).to_equal(200)
        expect(response.body).to_be_jpeg()

    @gen_test
    async def test_can_read_cmyk_jpeg_as_png(self):
        response = await self.async_fetch("/unsafe/filters:format(png)/cmyk.jpg")
        expect(response.code).to_equal(200)
        expect(response.body).to_be_png()

    @gen_test
    async def test_can_read_image_svg_with_px_units_and_convert_png(self):
        response = await self.async_fetch("/unsafe/Commons-logo.svg")
        expect(response.code).to_equal(200)
        expect(response.body).to_be_png()

        engine = Engine(self.context)
        engine.load(response.body, ".png")
        expect(engine.size).to_equal((1024, 1376))

    @gen_test
    async def test_can_read_image_svg_with_inch_units_and_convert_png(self):
        response = await self.async_fetch("/unsafe/Commons-logo-inches.svg")
        expect(response.code).to_equal(200)
        expect(response.body).to_be_png()

        engine = Engine(self.context)
        engine.load(response.body, ".png")
        expect(engine.size).to_equal((2000, 2600))

    @gen_test
    async def test_can_read_8bit_tiff_as_png(self):
        response = await self.async_fetch("/unsafe/gradient_8bit.tif")
        expect(response.code).to_equal(200)
        expect(response.body).to_be_png()

    @gen_test
    async def test_can_read_16bit_lsb_tiff_as_png(self):
        response = await self.async_fetch("/unsafe/gradient_lsb_16bperchannel.tif")
        expect(response.code).to_equal(200)
        expect(response.body).to_be_png()

    @gen_test
    async def test_can_read_16bit_msb_tiff_as_png(self):
        response = await self.async_fetch("/unsafe/gradient_msb_16bperchannel.tif")
        expect(response.code).to_equal(200)
        expect(response.body).to_be_png()


class ImageOperationsWithoutUnsafeTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.ALLOW_UNSAFE_URL = False

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8890, "localhost", "thumbor.conf", None, "info", None)
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    @gen_test
    async def test_can_get_image_with_signed_url(self):
        response = await self.async_fetch(
            "/_wIUeSaeHw8dricKG2MGhqu5thk=/smart/image.jpg"
        )
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(default_image())

    @gen_test
    async def test_getting_unsafe_image_fails(self):
        response = await self.async_fetch("/unsafe/smart/image.jpg")
        expect(response.code).to_equal(400)


class ImageOperationsWithStoredKeysTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="MYKEY")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.ALLOW_UNSAFE_URL = False
        cfg.STORES_CRYPTO_KEY_FOR_EACH_IMAGE = True

        cfg.STORAGE = "thumbor.storages.file_storage"
        cfg.STORAGE_FILE_STORAGE_ROOT_PATH = self.root_path

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8891, "localhost", "thumbor.conf", None, "info", None)
        server.security_key = "MYKEY"
        return Context(server, cfg, importer)

    @gen_test
    async def test_stored_security_key_with_regular_image(self):
        storage = self.context.modules.storage
        self.context.server.security_key = "MYKEY"
        await storage.put_crypto(
            "image.jpg"
        )  # Write a file on the file storage containing the security key
        self.context.server.security_key = "MYKEY2"

        try:
            response = await self.async_fetch(
                "/nty7gpBIRJ3GWtYDLLw6q1PgqTo=/smart/image.jpg"
            )
            expect(response.code).to_equal(200)
            expect(response.body).to_be_similar_to(default_image())
        finally:
            self.context.server.security_key = "MYKEY"

    @gen_test
    async def test_stored_security_key_with_regular_image_with_querystring(
        self,
    ):  # NOQA
        storage = self.context.modules.storage
        self.context.server.security_key = "MYKEY"
        await storage.put_crypto(
            "image.jpg%3Fts%3D1"
        )  # Write a file on the file storage containing the security key
        self.context.server.security_key = "MYKEY2"

        response = await self.async_fetch(
            "/Iw7LZGdr-hHj2gQ4ZzksP3llQHY=/smart/image.jpg%3Fts%3D1"
        )
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(default_image())

    @gen_test
    async def test_stored_security_key_with_regular_image_with_hash(self):
        storage = self.context.modules.storage
        self.context.server.security_key = "MYKEY"
        await storage.put_crypto(
            "image.jpg%23something"
        )  # Write a file on the file storage containing the security key
        self.context.server.security_key = "MYKEY2"

        response = await self.async_fetch(
            "/fxOHtHcTZMyuAQ1YPKh9KWg7nO8=/smart/image.jpg%23something"
        )
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(default_image())


class ImageOperationsWithAutoPngToJpgTestCase(BaseImagingTestCase):
    def get_config(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.AUTO_PNG_TO_JPG = True
        cfg.RESULT_STORAGE = "thumbor.result_storages.file_storage"
        cfg.RESULT_STORAGE_EXPIRATION_SECONDS = 60
        cfg.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = self.root_path
        return cfg

    def get_importer(self):
        importer = Importer(self.config)
        importer.import_modules()
        return importer

    def get_server(self):
        server = ServerParameters(8889, "localhost", "thumbor.conf", None, "info", None)
        server.security_key = "ACME-SEC"
        return server

    def get_request(self, *args, **kwargs):
        return RequestParameters(*args, **kwargs)

    def get_context(self):
        ctx = super(ImageOperationsWithAutoPngToJpgTestCase, self).get_context()
        ctx.request = self.get_request()
        return ctx

    async def get_as_webp(self, url):
        return await self.async_fetch(url, headers={"Accept": "image/webp,*/*;q=0.8"})

    @gen_test
    async def test_should_auto_convert_png_to_jpg(self):
        response = await self.async_fetch(
            "/unsafe/Giunchedi%2C_Filippo_January_2015_01.png"
        )
        expect(response.code).to_equal(200)
        expect(response.headers).not_to_include("Vary")
        expect(response.body).to_be_jpeg()

    @patch("thumbor.handlers.Context")
    @gen_test
    async def test_should_auto_convert_png_to_jpg_with_signed_images(
        self, context_mock
    ):
        context_mock.return_value = self.context
        crypto = CryptoURL("ACME-SEC")
        url = crypto.generate(image_url="Giunchedi%2C_Filippo_January_2015_01.png")
        self.context.request = self.get_request(url=url)

        context_mock.return_value = self.context
        response = await self.async_fetch(url)
        expect(response.code).to_equal(200)
        expect(response.headers).not_to_include("Vary")
        expect(response.body).to_be_jpeg()

    @gen_test
    async def test_shouldnt_auto_convert_png_to_jpg_if_png_has_transparency(
        self,
    ):  # NOQA
        response = await self.async_fetch("/unsafe/watermark.png")
        expect(response.code).to_equal(200)
        expect(response.headers).not_to_include("Vary")
        expect(response.body).to_be_png()

    @patch("thumbor.handlers.Context")
    @gen_test
    async def test_shouldnt_auto_convert_png_to_jpg_if_png_has_transparency_with_signed_images(  # NOQA
        self, context_mock
    ):
        context_mock.return_value = self.context
        crypto = CryptoURL("ACME-SEC")
        url = crypto.generate(image_url="watermark.png")
        self.context.request = self.get_request(url=url)

        # save on result storage
        response = await self.async_fetch(url)
        expect(response.code).to_equal(200)
        expect(response.headers).not_to_include("Vary")
        expect(response.body).to_be_png()

    @gen_test
    async def test_should_auto_convert_png_to_webp_if_auto_webp_is_true(self):
        self.config.AUTO_WEBP = True

        response = await self.get_as_webp(
            "/unsafe/Giunchedi%2C_Filippo_January_2015_01.png"
        )
        expect(response.code).to_equal(200)
        expect(response.headers).to_include("Vary")
        expect(response.body).to_be_webp()

    @patch("thumbor.handlers.Context")
    @gen_test
    async def test_should_auto_convert_png_to_webp_if_auto_webp_is_true_with_signed_images(  # NOQA
        self, context_mock
    ):
        self.config.AUTO_WEBP = True
        context_mock.return_value = self.context
        crypto = CryptoURL("ACME-SEC")
        url = crypto.generate(image_url="Giunchedi%2C_Filippo_January_2015_01.png")
        self.context.request = self.get_request(url=url, accepts_webp=True)

        # save on result storage
        response = await self.get_as_webp(url)
        expect(response.code).to_equal(200)
        expect(response.headers).to_include("Vary")
        expect(response.body).to_be_webp()

    @gen_test
    async def test_should_auto_convert_png_to_webp_if_auto_webp_is_true_and_png_has_transparency(  # NOQA
        self,
    ):
        self.config.AUTO_WEBP = True

        response = await self.get_as_webp("/unsafe/watermark.png")
        expect(response.code).to_equal(200)
        expect(response.headers).to_include("Vary")
        expect(response.body).to_be_webp()

    @patch("thumbor.handlers.Context")
    @gen_test
    async def test_should_auto_convert_png_to_webp_if_auto_webp_is_true_and_png_has_transparency_with_signed_images(  # NOQA
        self, context_mock
    ):
        self.config.AUTO_WEBP = True
        context_mock.return_value = self.context
        crypto = CryptoURL("ACME-SEC")
        url = crypto.generate(image_url="watermark.png")
        self.context.request = self.get_request(url=url)

        # save on result storage
        response = await self.get_as_webp(url)
        expect(response.code).to_equal(200)
        expect(response.headers).to_include("Vary")
        expect(response.body).to_be_webp()

    @patch("thumbor.handlers.imaging.RequestParameters")
    @gen_test
    async def test_shouldnt_auto_convert_png_to_jpg_if_requested_by_request_param(  # NOQA
        self, request_mock
    ):
        def side_effect(*_, **kwargs):
            req = RequestParameters(**kwargs)
            req.auto_png_to_jpg = False

            return req

        request_mock.side_effect = side_effect

        response = await self.async_fetch(
            "/unsafe/Giunchedi%2C_Filippo_January_2015_01.png"
        )
        expect(response.code).to_equal(200)
        expect(response.headers).not_to_include("Vary")
        expect(response.body).to_be_png()

    @patch("thumbor.handlers.imaging.RequestParameters")
    @gen_test
    async def test_should_auto_convert_png_to_jpg_if_requested_by_request_param(  # NOQA
        self, request_mock
    ):
        self.config.AUTO_PNG_TO_JPG = False

        def side_effect(*_, **kwargs):
            req = RequestParameters(**kwargs)
            req.auto_png_to_jpg = True

            return req

        request_mock.side_effect = side_effect

        response = await self.async_fetch(
            "/unsafe/Giunchedi%2C_Filippo_January_2015_01.png"
        )
        expect(response.code).to_equal(200)
        expect(response.headers).not_to_include("Vary")
        expect(response.body).to_be_jpeg()


class ImageOperationsWithAutoWebPTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.AUTO_WEBP = True

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, "localhost", "thumbor.conf", None, "info", None)
        server.security_key = "ACME-SEC"
        ctx = Context(server, cfg, importer)
        ctx.server.gifsicle_path = which("gifsicle")
        return ctx

    async def get_as_webp(self, url):
        return await self.async_fetch(url, headers={"Accept": "image/webp,*/*;q=0.8"})

    @gen_test
    async def test_can_auto_convert_jpeg(self):
        response = await self.get_as_webp("/unsafe/image.jpg")
        expect(response.code).to_equal(200)
        expect(response.headers).to_include("Vary")
        expect(response.headers["Vary"]).to_include("Accept")

        expect(response.body).to_be_webp()

    @gen_test
    async def test_should_not_convert_animated_gifs_to_webp(self):
        response = await self.get_as_webp("/unsafe/animated.gif")

        expect(response.code).to_equal(200)
        expect(response.headers).not_to_include("Vary")
        expect(response.body).to_be_gif()

    @gen_test
    async def test_should_convert_image_with_small_width_and_no_height(self):
        response = await self.get_as_webp("/unsafe/0x0:1681x596/1x/image.jpg")

        expect(response.code).to_equal(200)
        expect(response.headers).to_include("Vary")
        expect(response.headers["Vary"]).to_include("Accept")
        expect(response.body).to_be_webp()

    @gen_test
    async def test_should_convert_monochromatic_jpeg(self):
        response = await self.get_as_webp("/unsafe/grayscale.jpg")
        expect(response.code).to_equal(200)
        expect(response.headers).to_include("Vary")
        expect(response.headers["Vary"]).to_include("Accept")
        expect(response.body).to_be_webp()

    @gen_test
    async def test_should_convert_cmyk_jpeg(self):
        response = await self.get_as_webp("/unsafe/cmyk.jpg")
        expect(response.code).to_equal(200)
        expect(response.headers).to_include("Vary")
        expect(response.headers["Vary"]).to_include("Accept")
        expect(response.body).to_be_webp()

    @gen_test
    async def test_shouldnt_convert_cmyk_jpeg_if_format_specified(self):
        response = await self.get_as_webp("/unsafe/filters:format(png)/cmyk.jpg")
        expect(response.code).to_equal(200)
        expect(response.headers).not_to_include("Vary")
        expect(response.body).to_be_png()

    @gen_test
    async def test_shouldnt_convert_cmyk_jpeg_if_gif(self):
        response = await self.get_as_webp("/unsafe/filters:format(gif)/cmyk.jpg")
        expect(response.code).to_equal(200)
        expect(response.headers).not_to_include("Vary")
        expect(response.body).to_be_gif()

    @gen_test
    async def test_shouldnt_convert_if_format_specified(self):
        response = await self.get_as_webp("/unsafe/filters:format(gif)/image.jpg")
        expect(response.code).to_equal(200)
        expect(response.headers).not_to_include("Vary")
        expect(response.body).to_be_gif()

    @gen_test
    async def test_shouldnt_add_vary_if_format_specified(self):
        response = await self.get_as_webp("/unsafe/filters:format(webp)/image.jpg")
        expect(response.code).to_equal(200)
        expect(response.headers).not_to_include("Vary")
        expect(response.body).to_be_webp()

    @gen_test
    async def test_should_add_vary_if_format_invalid(self):
        response = await self.get_as_webp("/unsafe/filters:format(asdf)/image.jpg")
        expect(response.code).to_equal(200)
        expect(response.headers).to_include("Vary")
        expect(response.headers["Vary"]).to_include("Accept")
        expect(response.body).to_be_webp()

    @gen_test
    async def test_converting_return_etags(self):
        response = await self.get_as_webp("/unsafe/image.jpg")
        expect(response.headers).to_include("Etag")


class ImageOperationsWithAutoWebPWithResultStorageTestCase(BaseImagingTestCase):
    def get_request(self, *args, **kwargs):
        return RequestParameters(*args, **kwargs)

    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.RESULT_STORAGE = "thumbor.result_storages.file_storage"
        cfg.RESULT_STORAGE_EXPIRATION_SECONDS = 60
        cfg.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = self.root_path
        cfg.AUTO_WEBP = True

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, "localhost", "thumbor.conf", None, "info", None)
        server.security_key = "ACME-SEC"
        ctx = Context(server, cfg, importer)
        ctx.request = self.get_request()
        ctx.server.gifsicle_path = which("gifsicle")
        return ctx

    @property
    def result_storage(self):
        return self.context.modules.result_storage

    async def get_as_webp(self, url):
        return await self.async_fetch(url, headers={"Accept": "image/webp,*/*;q=0.8"})

    @patch("thumbor.handlers.Context")
    @gen_test
    async def test_can_auto_convert_jpeg_from_result_storage(
        self, context_mock
    ):  # NOQA
        context_mock.return_value = self.context
        crypto = CryptoURL("ACME-SEC")
        url = crypto.generate(image_url=quote("http://test.com/smart/image.jpg"))
        self.context.request = self.get_request(url=url, accepts_webp=True)
        with open("./tests/fixtures/images/image.webp", "rb") as fixture:
            await self.context.modules.result_storage.put(fixture.read())

        response = await self.get_as_webp(url)
        expect(response.code).to_equal(200)
        expect(response.headers).to_include("Vary")
        expect(response.headers["Vary"]).to_include("Accept")
        expect(response.body).to_be_webp()

    @patch("thumbor.handlers.Context")
    @gen_test
    async def test_can_auto_convert_unsafe_jpeg_from_result_storage(self, context_mock):
        context_mock.return_value = self.context
        self.context.request = self.get_request(accepts_webp=True)

        response = await self.get_as_webp("/unsafe/image.jpg")
        expect(response.code).to_equal(200)
        expect(response.headers).to_include("Vary")
        expect(response.headers["Vary"]).to_include("Accept")
        expect(response.body).to_be_webp()


class ImageOperationsWithoutEtagsTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.ENABLE_ETAGS = False

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, "localhost", "thumbor.conf", None, "info", None)
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    @gen_test
    async def test_can_get_image_without_etags(self):
        response = await self.async_fetch(
            "/unsafe/image.jpg", headers={"Accept": "image/webp,*/*;q=0.8"}
        )

        expect(response.code).to_equal(200)
        expect(response.headers).not_to_include("Etag")


class ImageOperationsWithLastModifiedTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path

        cfg.RESULT_STORAGE = "thumbor.result_storages.file_storage"
        cfg.RESULT_STORAGE_EXPIRATION_SECONDS = 60
        cfg.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = self.root_path

        cfg.SEND_IF_MODIFIED_LAST_MODIFIED_HEADERS = True

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, "localhost", "thumbor.conf", None, "info", None)
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    @property
    def result_storage(self):
        return self.context.modules.result_storage

    def write_image(self):
        expected_path = self.result_storage.normalize_path(
            "/_wIUeSaeHw8dricKG2MGhqu5thk=/smart/image.jpg"
        )

        if not os.path.exists(dirname(expected_path)):
            os.makedirs(dirname(expected_path))

        if not os.path.exists(expected_path):
            with open(expected_path, "wb") as img:
                img.write(default_image())

    @gen_test
    async def test_can_get_304_with_last_modified(self):
        self.write_image()
        response = await self.async_fetch(
            "/_wIUeSaeHw8dricKG2MGhqu5thk=/smart/image.jpg",
            headers={
                "Accept": "image/webp,*/*;q=0.8",
                "If-Modified-Since": (datetime.utcnow() + timedelta(seconds=1))
                .replace(tzinfo=pytz.utc)
                .strftime("%a, %d %b %Y %H:%M:%S GMT"),  # NOW +1 sec UTC
            },
        )

        expect(response.code).to_equal(304)

    @gen_test
    async def test_can_get_image_with_last_modified(self):
        self.write_image()
        response = await self.async_fetch(
            "/_wIUeSaeHw8dricKG2MGhqu5thk=/smart/image.jpg",
            headers={
                "Accept": "image/webp,*/*;q=0.8",
                "If-Modified-Since": (datetime.utcnow() - timedelta(days=365))
                .replace(tzinfo=pytz.utc)
                .strftime("%a, %d %b %Y %H:%M:%S GMT"),  # Last Year
            },
        )

        expect(response.code).to_equal(200)
        expect(response.headers).to_include("Last-Modified")


class ImageOperationsWithGifVTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.FFMPEG_PATH = which("ffmpeg")
        cfg.OPTIMIZERS = [
            "thumbor.optimizers.gifv",
        ]

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, "localhost", "thumbor.conf", None, "info", None)
        server.security_key = "ACME-SEC"
        ctx = Context(server, cfg, importer)
        ctx.server.gifsicle_path = which("gifsicle")
        return ctx

    @gen_test
    async def test_should_convert_animated_gif_to_mp4_when_filter_without_params(  # NOQA
        self,
    ):
        response = await self.async_fetch("/unsafe/filters:gifv()/animated.gif")

        expect(response.code).to_equal(200)
        expect(response.headers["Content-Type"]).to_equal("video/mp4")

    @gen_test
    async def test_should_convert_animated_gif_to_webm_when_filter_with_gifv_webm_param(  # NOQA
        self,
    ):
        response = await self.async_fetch("/unsafe/filters:gifv(webm)/animated.gif")

        expect(response.code).to_equal(200)
        expect(response.headers["Content-Type"]).to_equal("video/webm")

    @gen_test
    async def test_should_convert_animated_gif_to_mp4_with_filter_without_params(  # NOQA
        self,
    ):
        response = await self.async_fetch(
            "/unsafe/filters:gifv(mp4):background_color(ff00ff)/animated.gif"
        )

        expect(response.code).to_equal(200)
        expect(response.headers["Content-Type"]).to_equal("video/mp4")


class ImageOperationsImageCoverTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.AUTO_WEBP = True
        cfg.USE_GIFSICLE_ENGINE = True

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, "localhost", "thumbor.conf", None, "info", None)
        server.security_key = "ACME-SEC"
        ctx = Context(server, cfg, importer)
        ctx.server.gifsicle_path = which("gifsicle")
        return ctx

    @gen_test
    async def test_can_get_image_cover(self):
        response = await self.async_fetch("/unsafe/filters:cover()/animated.gif")

        expect(response.code).to_equal(200)
        expect(response.headers["Content-Type"]).to_equal("image/gif")


class ImageOperationsWithResultStorageTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path

        cfg.RESULT_STORAGE = "thumbor.result_storages.file_storage"
        cfg.RESULT_STORAGE_EXPIRATION_SECONDS = 60
        cfg.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = self.root_path

        cfg.USE_GIFSICLE_ENGINE = True
        cfg.FFMPEG_PATH = which("ffmpeg")
        cfg.AUTO_WEBP = True
        cfg.OPTIMIZERS = [
            "thumbor.optimizers.gifv",
        ]

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, "localhost", "thumbor.conf", None, "info", None)
        server.security_key = "ACME-SEC"
        ctx = Context(server, cfg, importer)
        ctx.server.gifsicle_path = which("gifsicle")

        return ctx

    @property
    def result_storage(self):
        return self.context.modules.result_storage

    @patch("tornado.ioloop.IOLoop.instance")
    @gen_test
    async def test_saves_image_to_result_storage(self, instance_mock):
        instance_mock.return_value = self.io_loop
        response = await self.async_fetch("/gTr2Xr9lbzIa2CT_dL_O0GByeR0=/animated.gif")
        expect(response.code).to_equal(200)

        self.context.request = Mock(accepts_webp=False,)
        expected_path = self.result_storage.normalize_path(
            "/gTr2Xr9lbzIa2CT_dL_O0GByeR0=/animated.gif"
        )
        expect(expected_path).to_exist()
        expect(response.body).to_be_similar_to(animated_image())


class ImageOperationsResultStorageOnlyTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = "/path/that/does/not/exist"

        cfg.RESULT_STORAGE = "thumbor.result_storages.file_storage"
        cfg.RESULT_STORAGE_EXPIRATION_SECONDS = 60
        cfg.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = self.root_path
        cfg.FFMPEG_PATH = which("ffmpeg")

        cfg.USE_GIFSICLE_ENGINE = True
        cfg.AUTO_WEBP = True
        cfg.OPTIMIZERS = [
            "thumbor.optimizers.gifv",
        ]

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, "localhost", "thumbor.conf", None, "info", None)
        server.security_key = "ACME-SEC"
        ctx = Context(server, cfg, importer)
        ctx.server.gifsicle_path = which("gifsicle")

        return ctx

    @property
    def result_storage(self):
        return self.context.modules.result_storage

    @gen_test
    async def test_loads_image_from_result_storage(self):
        self.context.request = Mock(accepts_webp=False,)
        expected_path = self.result_storage.normalize_path(
            "gTr2Xr9lbzIa2CT_dL_O0GByeR0=/animated.gif"
        )
        os.makedirs(dirname(expected_path))
        with open(expected_path, "wb") as img:
            img.write(animated_image())

        response = await self.async_fetch("/gTr2Xr9lbzIa2CT_dL_O0GByeR0=/animated.gif")
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(animated_image())

    @patch.object(FileResultStorage, "get", side_effect=Exception)
    @gen_test
    async def test_loads_image_from_result_storage_fails_on_exception(self, _):
        response = await self.async_fetch("/gTr2Xr9lbzIa2CT_dL_O0GByeR0=/animated.gif")
        expect(response.code).to_equal(500)
        expect(response.body).to_be_empty()


class ImageOperationsWithGifWithoutGifsicle(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path

        cfg.RESULT_STORAGE = "thumbor.result_storages.file_storage"
        cfg.RESULT_STORAGE_EXPIRATION_SECONDS = 60
        cfg.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = self.root_path
        cfg.AUTO_WEBP = True

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, "localhost", "thumbor.conf", None, "info", None)
        server.security_key = "ACME-SEC"
        ctx = Context(server, cfg, importer)

        return ctx

    @gen_test
    async def test_should_be_ok_with_single_frame_gif(self):
        response = await self.async_fetch(
            "/5Xr8gyuWE7jL_VB72K0wvzTMm2U=/animated-one-frame.gif"
        )

        expect(response.code).to_equal(200)
        expect(response.headers["Content-Type"]).to_equal("image/gif")
        expect(response.body).to_be_similar_to(not_so_animated_image())


class ImageOperationsWithGifWithoutGifsicleOnResultStorage(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = "/path/that/does/not/exist"

        cfg.RESULT_STORAGE = "thumbor.result_storages.file_storage"
        cfg.RESULT_STORAGE_EXPIRATION_SECONDS = 60
        cfg.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = self.root_path

        cfg.AUTO_WEBP = True

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, "localhost", "thumbor.conf", None, "info", None)
        server.security_key = "ACME-SEC"
        ctx = Context(server, cfg, importer)

        return ctx

    @property
    def result_storage(self):
        return self.context.modules.result_storage

    @gen_test
    async def test_loads_image_from_result_storage(self):
        self.context.request = Mock(accepts_webp=False,)
        expected_path = self.result_storage.normalize_path(
            "5Xr8gyuWE7jL_VB72K0wvzTMm2U=/animated-one-frame.gif"
        )
        os.makedirs(dirname(expected_path))
        with open(expected_path, "wb") as img:
            img.write(not_so_animated_image())

        response = await self.async_fetch(
            "/5Xr8gyuWE7jL_VB72K0wvzTMm2U=/animated-one-frame.gif"
        )
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(not_so_animated_image())


class ImageOperationsWithMaxWidthAndMaxHeight(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path

        cfg.RESULT_STORAGE = "thumbor.result_storages.file_storage"
        cfg.RESULT_STORAGE_EXPIRATION_SECONDS = 60
        cfg.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = self.root_path
        cfg.AUTO_WEBP = True
        cfg.MAX_WIDTH = 150
        cfg.MAX_HEIGHT = 150

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, "localhost", "thumbor.conf", None, "info", None)
        server.security_key = "ACME-SEC"
        ctx = Context(server, cfg, importer)

        return ctx

    @gen_test
    async def test_should_be_ok_but_150x150(self):
        response = await self.async_fetch("/unsafe/200x200/grayscale.jpg")
        engine = Engine(self.context)
        engine.load(response.body, ".jpg")
        expect(response.code).to_equal(200)
        expect(response.headers["Content-Type"]).to_equal("image/jpeg")
        expect(engine.size).to_equal((150, 150))


class ImageOperationsWithMaxPixels(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.MAX_PIXELS = 1000

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, "localhost", "thumbor.conf", None, "info", None)
        server.security_key = "ACME-SEC"
        ctx = Context(server, cfg, importer)
        ctx.server.gifsicle_path = which("gifsicle")
        return ctx

    @gen_test
    async def test_should_error(self):
        response = await self.async_fetch("/unsafe/200x200/grayscale.jpg")
        expect(response.code).to_equal(400)


class ImageOperationsWithRespectOrientation(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.RESPECT_ORIENTATION = True
        cfg.PRESERVE_EXIF_INFO = True

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, "localhost", "thumbor.conf", None, "info", None)
        server.security_key = "ACME-SEC"
        self.context = Context(server, cfg, importer)
        self.context.server.gifsicle_path = which("gifsicle")
        return self.context

    @gen_test
    async def test_should_be_ok_when_orientation_exif(self):
        response = await self.async_fetch(
            "/unsafe/10_years_of_Wikipedia_by_Guillaume_Paumier.jpg"
        )
        expect(response.code).to_equal(200)
        engine = Engine(self.context)
        engine.load(response.body, ".jpg")
        expect(engine.size).to_equal((4052, 3456))

    @gen_test
    async def test_should_be_ok_without_orientation_exif(self):
        response = await self.async_fetch("/unsafe/20x20.jpg")
        expect(response.code).to_equal(200)
        engine = Engine(self.context)
        engine.load(response.body, ".jpg")
        expect(engine.size).to_equal((20, 20))


class EngineLoadException(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.FILTERS = []

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, "localhost", "thumbor.conf", None, "info", None)
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    @patch.object(Engine, "load", side_effect=ValueError)
    @gen_test
    async def test_should_error_on_engine_load_exception(self, _):
        response = await self.async_fetch("/unsafe/image.jpg")
        expect(response.code).to_equal(500)

    @pytest.mark.skip(
        reason="I disagree with this test. If the engine fails we "
        "should get an error, otherwise we may end up caching an invalid crop."
    )
    @gen_test
    async def test_should_release_ioloop_on_error_on_engine_exception(self):
        response = await self.async_fetch("/unsafe/fit-in/134x134/940x2.png")
        expect(response.code).to_equal(200)

    @pytest.mark.skip(
        reason="I disagree with this test. If the engine fails we "
        "should get an error, otherwise we may end up caching an invalid crop."
    )
    @gen_test
    async def test_should_exec_other_operations_on_error_on_engine_exception(
        self,
    ):  # NOQA
        response = await self.async_fetch(
            "/unsafe/fit-in/134x134/filters:equalize()/940x2.png"
        )
        expect(response.code).to_equal(200)

    @patch.object(Engine, "read", side_effect=Exception)
    @gen_test
    async def test_should_fail_with_500_upon_engine_read_exception(self, _):  # NOQA
        response = await self.async_fetch("/unsafe/fit-in/134x134/940x2.png")
        expect(response.code).to_equal(500)


class StorageOverride(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.file_storage"
        cfg.FILE_STORAGE_ROOT_PATH = self.root_path

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, "localhost", "thumbor.conf", None, "info", None)
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    @gen_test
    async def test_shouldnt_call_put_when_storage_overridden_to_nostorage(
        self,
    ):  # NOQA
        old_load = Engine.load
        old_put = FileStorage.put

        def load_override(self, arg, arg2):
            self.context.modules.storage = NoStorage(None)
            return old_load(self, arg, arg2)

        def put_override(*_):
            expect.not_to_be_here()

        Engine.load = load_override
        FileStorage.put = put_override

        response = await self.async_fetch("/unsafe/image.jpg")

        Engine.load = old_load
        FileStorage.put = old_put

        expect(response.code).to_equal(200)


@pytest.mark.skipif(
    not JPEGTRAN_AVAILABLE or not EXIFTOOL_AVAILABLE,
    reason="In order to run thumbor's tests please install both jpegtran and exiftool",
)
class ImageOperationsWithJpegtranTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.JPEGTRAN_PATH = which("jpegtran")
        cfg.PROGRESSIVE_JPEG = (True,)
        cfg.RESULT_STORAGE_STORES_UNSAFE = (True,)
        cfg.OPTIMIZERS = [
            "thumbor.optimizers.jpegtran",
        ]

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, "localhost", "thumbor.conf", None, "info", None)
        server.security_key = "ACME-SEC"
        ctx = Context(server, cfg, importer)
        return ctx

    @gen_test
    async def test_should_optimize_jpeg(self):
        response = await self.async_fetch("/unsafe/200x200/image.jpg")

        tmp_fd, tmp_file_path = tempfile.mkstemp(suffix=".jpg")
        fixture = os.fdopen(tmp_fd, "wb")
        fixture.write(response.body)
        fixture.close()

        exiftool = which("exiftool")
        if not exiftool:
            raise AssertionError(
                "exiftool was not found. Please install it to run thumbor's tests."
            )

        command = [exiftool, tmp_file_path, "-DeviceModel", "-EncodingProcess"]

        try:
            output = subprocess.check_output(command, stdin=subprocess.DEVNULL)

            expect(response.code).to_equal(200)
            expect(output).to_equal(
                "Encoding Process                : Progressive DCT, Huffman coding\n"
            )
        finally:
            os.remove(tmp_file_path)

    @gen_test
    async def test_with_meta(self):
        response = await self.async_fetch("/unsafe/meta/800x400/image.jpg")
        expect(response.code).to_equal(200)

    @gen_test
    async def test_with_meta_cached(self):
        await self.async_fetch("/unsafe/meta/800x400/image.jpg")
        response = await self.async_fetch("/unsafe/meta/800x400/image.jpg")
        expect(response.code).to_equal(200)


class ImageOperationsWithoutStorage(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.AUTO_WEBP = True
        cfg.USE_GIFSICLE_ENGINE = True
        cfg.RESPECT_ORIENTATION = True

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, "localhost", "thumbor.conf", None, "info", None)
        server.security_key = "ACME-SEC"
        ctx = Context(server, cfg, importer)
        ctx.server.gifsicle_path = which("gifsicle")
        return ctx

    @gen_test
    async def test_meta(self):
        response = await self.async_fetch("/unsafe/meta/800x400/image.jpg")
        expect(response.code).to_equal(200)

    @gen_test
    async def test_meta_with_unicode(self):
        response = await self.async_fetch(
            "/unsafe/meta/200x300/alabama1_ap620%C3%A9.jpg"
        )
        expect(response.code).to_equal(200)
        obj = loads(response.body.decode("utf-8"))
        expect(obj["thumbor"]["target"]["width"]).to_equal(200)
        expect(obj["thumbor"]["target"]["height"]).to_equal(300)

    @gen_test
    async def test_meta_frame_count(self):
        response = await self.async_fetch("/unsafe/meta/800x400/image.jpg")
        expect(response.code).to_equal(200)
        obj = loads(response.body.decode("utf-8"))
        expect(obj["thumbor"]["source"]["frameCount"]).to_equal(1)

    @gen_test
    async def test_meta_frame_count_with_gif(self):
        response = await self.async_fetch("/unsafe/meta/animated.gif")
        expect(response.code).to_equal(200)
        obj = loads(response.body.decode("utf-8"))
        expect(obj["thumbor"]["source"]["frameCount"]).to_equal(2)

    @gen_test
    async def test_max_bytes(self):
        response = await self.async_fetch(
            "/unsafe/filters:max_bytes(35000)/Giunchedi%2C_"
            "Filippo_January_2015_01.jpg"
        )
        expect(response.code).to_equal(200)
        expect(len(response.body)).to_be_lesser_or_equal_to(35000)

    @gen_test
    async def test_max_bytes_impossible(self):
        response = await self.async_fetch(
            "/unsafe/filters:max_bytes(1000)/Giunchedi%2C_Filippo_"
            "January_2015_01.jpg"
        )
        expect(response.code).to_equal(200)
        expect(len(response.body)).to_be_greater_than(1000)

    @gen_test
    async def test_meta_with_exif_orientation(self):
        response = await self.async_fetch(
            "/unsafe/meta/0x0/Giunchedi%2C_Filippo_January_2015_01-"
            "cmyk-orientation-exif.jpg"
        )
        expect(response.code).to_equal(200)
        obj = loads(response.body.decode("utf-8"))
        expect(obj["thumbor"]["target"]["width"]).to_equal(533)
        expect(obj["thumbor"]["target"]["height"]).to_equal(800)


class TranslateCoordinatesTestCase(TestCase):
    def setUp(self):
        super(TranslateCoordinatesTestCase, self).setUp()
        coords = self.get_coords()
        crop_coords = BaseHandler.translate_crop_coordinates(
            original_width=coords["original_width"],
            original_height=coords["original_height"],
            width=coords["width"],
            height=coords["height"],
            crop_left=coords["crop_left"],
            crop_top=coords["crop_top"],
            crop_right=coords["crop_right"],
            crop_bottom=coords["crop_bottom"],
        )
        self.translate_crop_coordinates = crop_coords

    def get_coords(self):
        return {
            "original_width": 3000,
            "original_height": 2000,
            "width": 1200,
            "height": 800,
            "crop_left": 100,
            "crop_top": 100,
            "crop_right": 200,
            "crop_bottom": 200,
            "expected_crop": (40, 40, 80, 80),
        }

    @gen_test
    async def test_should_be_a_list_of_coords(self):
        expect(self.translate_crop_coordinates).to_be_instance_of(tuple)

    @gen_test
    async def test_should_translate_from_original_to_resized(self):
        expect(self.translate_crop_coordinates).to_equal(
            self.get_coords()["expected_crop"]
        )


class ImageBadRequestDecompressionBomb(TestCase):
    def setUp(self):
        self.root_path = tempfile.mkdtemp()
        self.loader_path = abspath(join(dirname(__file__), "../fixtures/images/"))
        self.base_uri = "/image"
        super(ImageBadRequestDecompressionBomb, self).setUp()

    def tearDown(self):
        shutil.rmtree(self.root_path)

    async def get_as_webp(self, url):
        return await self.async_fetch(url, headers={"Accept": "image/webp,*/*;q=0.8"})

    def get_config(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.AUTO_WEBP = True
        return cfg

    def get_server(self):
        server = ServerParameters(8889, "localhost", "thumbor.conf", None, "info", None)
        validate_config(self.config, server)
        return server

    def get_importer(self):
        importer = Importer(self.config)
        importer.import_modules()
        return importer

    @gen_test
    async def test_should_bad_request_if_bigger_than_75_megapixels(self):
        response = await self.get_as_webp("/unsafe/16384x16384.png")
        expect(response.code).to_equal(400)

    @gen_test
    async def test_should_bad_request_if_bigger_than_75_megapixels_jpeg(self):
        response = await self.get_as_webp("/unsafe/9643x10328.jpg")
        expect(response.code).to_equal(400)


class LoaderErrorTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.file_storage"
        cfg.FILE_STORAGE_ROOT_PATH = self.root_path

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, "localhost", "thumbor.conf", None, "info", None)
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    @gen_test
    async def test_should_propagate_custom_loader_error(self):
        old_load = self.context.modules.loader.load

        async def load_override(*_):
            result = LoaderResult()
            result.successful = False
            result.error = 409
            return result

        self.context.modules.loader.load = load_override

        response = await self.async_fetch("/unsafe/image.jpg")

        self.context.modules.loader.load = old_load

        expect(response.code).to_equal(409)
