#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import shutil
import tempfile
from os.path import abspath, dirname, join
from shutil import which
from urllib.parse import quote

from preggy import expect
import tornado.web
from tornado.testing import gen_test
from tests.fixtures.images import (
    alabama1,
    default_image,
    invalid_quantization,
    space_image,
)

from tests.base import TestCase
from thumbor.handlers import BaseHandler
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.engines.pil import Engine
from thumbor.importer import Importer

# pylint: disable=broad-except,abstract-method,attribute-defined-outside-init,line-too-long,too-many-public-methods
# pylint: disable=too-many-lines

JPEGTRAN_AVAILABLE = which("jpegtran") is not None
EXIFTOOL_AVAILABLE = which("exiftool") is not None


class ErrorHandler(BaseHandler):
    def get(self):
        self._error(403)


class BaseHandlerTestApp(tornado.web.Application):
    def __init__(self, context):
        self.context = context
        super().__init__([(r"/error", ErrorHandler)])


class BaseImagingTestCase(TestCase):
    def setUp(self):
        self.root_path = tempfile.mkdtemp()
        self.loader_path = abspath(join(dirname(__file__), "../fixtures/images/"))
        self.base_uri = "/image"
        super().setUp()

    def tearDown(self):
        shutil.rmtree(self.root_path)


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
