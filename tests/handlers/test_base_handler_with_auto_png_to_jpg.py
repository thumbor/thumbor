#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from unittest.mock import patch

from libthumbor import CryptoURL
from preggy import expect
from tornado.testing import gen_test

from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import RequestParameters, ServerParameters
from thumbor.importer import Importer

# pylint: disable=broad-except,abstract-method,attribute-defined-outside-init,line-too-long,too-many-public-methods
# pylint: disable=too-many-lines


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
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return server

    def get_request(self, *args, **kwargs):
        return RequestParameters(*args, **kwargs)

    def get_context(self):
        ctx = super().get_context()
        ctx.request = self.get_request()
        return ctx

    async def get_as_webp(self, url):
        return await self.async_fetch(
            url, headers={"Accept": "image/webp,*/*;q=0.8"}
        )

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
        url = crypto.generate(
            image_url="Giunchedi%2C_Filippo_January_2015_01.png"
        )
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
        url = crypto.generate(
            image_url="Giunchedi%2C_Filippo_January_2015_01.png"
        )
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
