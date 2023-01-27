#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import logging
import shutil
import tempfile
from os.path import abspath, dirname, join
from shutil import which
from unittest import mock
from urllib.parse import quote

import pytest
import tornado.web
from preggy import expect
from tornado.testing import gen_test

import thumbor.engines.pil
from tests.base import TestCase, skip_unless_avif, skip_unless_heif
from tests.fixtures.images import (
    alabama1,
    default_image,
    invalid_quantization,
    space_image,
)
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.engines.pil import Engine
from thumbor.handlers import BaseHandler
from thumbor.importer import Importer

JPEGTRAN_AVAILABLE = which("jpegtran") is not None
EXIFTOOL_AVAILABLE = which("exiftool") is not None


@pytest.fixture(scope="function")
def unittest_caplog(request, caplog):
    request.function.__self__.caplog = caplog


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
        self.loader_path = abspath(
            join(dirname(__file__), "../fixtures/images/")
        )
        self.base_uri = "/image"
        super().setUp()

    def tearDown(self):
        shutil.rmtree(self.root_path)


class ImagingOperationsTestCase(BaseImagingTestCase):
    caplog = None  # can be added by unittest_caplog fixture

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
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
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
        enc_url = quote(
            "15967251_212831_19242645_АгатавЗоопарке.jpg".encode("utf-8")
        )
        response = await self.async_fetch(f"/unsafe/{enc_url}")
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
        response = await self.async_fetch("/unsafe/image%20space.jpg")
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
        response = await self.async_fetch(
            "/unsafe/filters:format(png)/cmyk.jpg"
        )
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
    async def test_svg_with_px_units_and_convert_to_png_with_size(self):
        width, height = 400, 500
        self.context.request = mock.Mock(width=width, height=height)
        response = await self.async_fetch(
            f"/unsafe/{width}x{height}/Commons-logo.svg"
        )
        expect(response.code).to_equal(200)
        expect(response.body).to_be_png()

        engine = Engine(self.context)
        engine.load(response.body, ".png")
        expect(engine.size).to_equal((width, height))

    @gen_test
    async def test_svg_with_inch_units_and_convert_to_png_with_size(self):
        width, height = 400, 500
        self.context.request = mock.Mock(width=width, height=height)
        response = await self.async_fetch(
            f"/unsafe/{width}x{height}/Commons-logo-inches.svg"
        )
        expect(response.code).to_equal(200)
        expect(response.body).to_be_png()

        engine = Engine(self.context)
        engine.load(response.body, ".png")
        expect(engine.size).to_equal((width, height))

    @gen_test
    async def test_svg_with_px_units_and_convert_to_png_with_width(self):
        width = 300
        self.context.request = mock.Mock(width=width)
        response = await self.async_fetch(
            f"/unsafe/fit-in/{width}x/Commons-logo.svg"
        )
        expect(response.code).to_equal(200)
        expect(response.body).to_be_png()

        engine = Engine(self.context)
        engine.load(response.body, ".png")
        expect(engine.size).to_equal((width, 403))

    @gen_test
    async def test_can_read_8bit_tiff_as_png(self):
        response = await self.async_fetch("/unsafe/gradient_8bit.tif")
        expect(response.code).to_equal(200)
        expect(response.body).to_be_png()

    @gen_test
    async def test_can_read_16bit_lsb_tiff_as_png(self):
        response = await self.async_fetch(
            "/unsafe/gradient_lsb_16bperchannel.tif"
        )
        expect(response.code).to_equal(200)
        expect(response.body).to_be_png()

    @gen_test
    async def test_can_read_16bit_msb_tiff_as_png(self):
        response = await self.async_fetch(
            "/unsafe/gradient_msb_16bperchannel.tif"
        )
        expect(response.code).to_equal(200)
        expect(response.body).to_be_png()

    @skip_unless_avif
    @gen_test
    async def test_avif_format(self):
        response = await self.async_fetch(
            "/unsafe/filters:format(avif)/image.jpg"
        )
        expect(response.code).to_equal(200)
        expect(response.body).to_be_avif()

    @gen_test
    @pytest.mark.usefixtures("unittest_caplog")
    async def test_avif_unavailable_format_jpg(self):
        self.caplog.set_level(logging.WARNING)
        with mock.patch.object(thumbor.engines.pil, "HAVE_AVIF", False):
            response = await self.async_fetch(
                "/unsafe/filters:format(avif)/image.jpg"
            )
            expect(response.code).to_equal(200)
            expect(response.body).to_be_jpeg()
            assert self.caplog.record_tuples == [
                (
                    "thumbor",
                    logging.WARNING,
                    "[PILEngine] AVIF encoding unavailable, defaulting to .jpg",
                )
            ]

    @gen_test
    @pytest.mark.usefixtures("unittest_caplog")
    async def test_avif_unavailable_format_png(self):
        self.caplog.set_level(logging.WARNING)
        with mock.patch.object(thumbor.engines.pil, "HAVE_AVIF", False):
            response = await self.async_fetch(
                "/unsafe/filters:format(avif)/1x1.png"
            )
            expect(response.code).to_equal(200)
            expect(response.body).to_be_png()
            assert self.caplog.record_tuples == [
                (
                    "thumbor",
                    logging.WARNING,
                    "[PILEngine] AVIF encoding unavailable, defaulting to .png",
                )
            ]

    @skip_unless_avif
    @gen_test
    async def test_avif_quality_setting(self):
        self.context.config.QUALITY = 80
        self.context.config.AVIF_QUALITY = 50
        with mock.patch.object(
            Engine,
            "read",
            autospec=True,
            side_effect=Engine.read,
        ) as mock_read:
            response = await self.async_fetch(
                "/unsafe/filters:format(avif)/image.jpg"
            )
            expect(response.code).to_equal(200)
            expect(response.body).to_be_avif()
            mock_read.assert_called_with(mock.ANY, ".avif", 50)

    @gen_test
    async def test_can_read_heif(self):
        response = await self.async_fetch("/unsafe/image.heic")
        expect(response.code).to_equal(200)
        expect(response.body).to_be_heif()

    @skip_unless_heif
    @gen_test
    async def test_heif_format(self):
        response = await self.async_fetch(
            "/unsafe/filters:format(heic)/image.jpg"
        )
        expect(response.code).to_equal(200)
        expect(response.body).to_be_heif()

    @skip_unless_heif
    @gen_test
    async def test_heif_quality_setting(self):
        self.context.config.QUALITY = 80
        self.context.config.HEIF_QUALITY = 50
        with mock.patch.object(
            Engine,
            "read",
            autospec=True,
            side_effect=Engine.read,
        ) as mock_read:
            response = await self.async_fetch(
                "/unsafe/filters:format(heif)/image.jpg"
            )
            expect(response.code).to_equal(200)
            expect(response.body).to_be_heif()
            mock_read.assert_called_with(mock.ANY, ".heif", 50)

    @gen_test
    @pytest.mark.usefixtures("unittest_caplog")
    async def test_heif_unavailable_format_jpg(self):
        self.caplog.set_level(logging.WARNING)
        with mock.patch.object(thumbor.engines.pil, "HAVE_HEIF", False):
            response = await self.async_fetch(
                "/unsafe/filters:format(heif)/image.jpg"
            )
            expect(response.code).to_equal(200)
            expect(response.body).to_be_jpeg()
            assert self.caplog.record_tuples == [
                (
                    "thumbor",
                    logging.WARNING,
                    "[PILEngine] HEIF encoding unavailable, defaulting to .jpg",
                )
            ]

    @gen_test
    @pytest.mark.usefixtures("unittest_caplog")
    async def test_heif_unavailable_format_png(self):
        self.caplog.set_level(logging.WARNING)
        with mock.patch.object(thumbor.engines.pil, "HAVE_HEIF", False):
            response = await self.async_fetch(
                "/unsafe/filters:format(heif)/1x1.png"
            )
            expect(response.code).to_equal(200)
            expect(response.body).to_be_png()
            assert self.caplog.record_tuples == [
                (
                    "thumbor",
                    logging.WARNING,
                    "[PILEngine] HEIF encoding unavailable, defaulting to .png",
                )
            ]
