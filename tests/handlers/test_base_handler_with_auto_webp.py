#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from shutil import which
from unittest.mock import patch
from urllib.parse import quote

from libthumbor import CryptoURL
from preggy import expect
from tornado.testing import gen_test

from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, RequestParameters, ServerParameters
from thumbor.importer import Importer

# pylint: disable=broad-except,abstract-method,attribute-defined-outside-init,line-too-long,too-many-public-methods
# pylint: disable=too-many-lines


class ImageOperationsWithAutoWebPTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.AUTO_WEBP = True

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        ctx = Context(server, cfg, importer)
        ctx.server.gifsicle_path = which("gifsicle")
        return ctx

    async def get_as_webp(self, url):
        return await self.async_fetch(
            url, headers={"Accept": "image/webp,*/*;q=0.8"}
        )

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
        response = await self.get_as_webp(
            "/unsafe/filters:format(png)/cmyk.jpg"
        )
        expect(response.code).to_equal(200)
        expect(response.headers).not_to_include("Vary")
        expect(response.body).to_be_png()

    @gen_test
    async def test_shouldnt_convert_cmyk_jpeg_if_gif(self):
        response = await self.get_as_webp(
            "/unsafe/filters:format(gif)/cmyk.jpg"
        )
        expect(response.code).to_equal(200)
        expect(response.headers).not_to_include("Vary")
        expect(response.body).to_be_gif()

    @gen_test
    async def test_shouldnt_convert_if_format_specified(self):
        response = await self.get_as_webp(
            "/unsafe/filters:format(gif)/image.jpg"
        )
        expect(response.code).to_equal(200)
        expect(response.headers).not_to_include("Vary")
        expect(response.body).to_be_gif()

    @gen_test
    async def test_shouldnt_add_vary_if_format_specified(self):
        response = await self.get_as_webp(
            "/unsafe/filters:format(webp)/image.jpg"
        )
        expect(response.code).to_equal(200)
        expect(response.headers).not_to_include("Vary")
        expect(response.body).to_be_webp()

    @gen_test
    async def test_should_add_vary_if_format_invalid(self):
        response = await self.get_as_webp(
            "/unsafe/filters:format(asdf)/image.jpg"
        )
        expect(response.code).to_equal(200)
        expect(response.headers).to_include("Vary")
        expect(response.headers["Vary"]).to_include("Accept")
        expect(response.body).to_be_webp()

    @gen_test
    async def test_converting_return_etags(self):
        response = await self.get_as_webp("/unsafe/image.jpg")
        expect(response.headers).to_include("Etag")


class ImageOperationsWithAutoWebPWithResultStorageTestCase(
    BaseImagingTestCase
):
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
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        ctx = Context(server, cfg, importer)
        ctx.request = self.get_request()
        ctx.server.gifsicle_path = which("gifsicle")
        return ctx

    @property
    def result_storage(self):
        return self.context.modules.result_storage

    async def get_as_webp(self, url):
        return await self.async_fetch(
            url, headers={"Accept": "image/webp,*/*;q=0.8"}
        )

    @patch("thumbor.handlers.Context")
    @gen_test
    async def test_can_auto_convert_jpeg_from_result_storage(
        self, context_mock
    ):  # NOQA
        context_mock.return_value = self.context
        crypto = CryptoURL("ACME-SEC")
        url = crypto.generate(
            image_url=quote("http://test.com/smart/image.jpg")
        )
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
    async def test_can_auto_convert_unsafe_jpeg_from_result_storage(
        self, context_mock
    ):
        context_mock.return_value = self.context
        self.context.request = self.get_request(accepts_webp=True)

        response = await self.get_as_webp("/unsafe/image.jpg")
        expect(response.code).to_equal(200)
        expect(response.headers).to_include("Vary")
        expect(response.headers["Vary"]).to_include("Accept")
        expect(response.body).to_be_webp()
