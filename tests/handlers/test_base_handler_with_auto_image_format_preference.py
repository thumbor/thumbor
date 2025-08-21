# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2025 globo.com thumbor@googlegroups.com

from shutil import which

from tornado.testing import gen_test
from preggy import expect

from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.importer import Importer


class ImageOperationsWithAutoImageFormatPreferenceTestCase(
    BaseImagingTestCase
):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.AUTO_WEBP = True
        cfg.AUTO_AVIF = True
        cfg.AUTO_IMAGE_FORMAT_PREFERENCE = "avif,webp,jpg,png"

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        ctx = Context(server, cfg, importer)
        ctx.server.gifsicle_path = which("gifsicle")
        return ctx

    async def get_as_webp_first(self, url):
        return await self.async_fetch(
            url, headers={"Accept": "image/webp,image/avif,*/*;q=0.8"}
        )

    @gen_test
    async def test_can_auto_convert_to_avif(self):
        response = await self.get_as_webp_first("/unsafe/image.jpg")
        expect(response.code).to_equal(200)
        expect(response.headers).to_include("Vary")
        expect(response.headers["Vary"]).to_include("Accept")

        expect(response.body).to_be_avif()


class ImageOperationsWithoutAutoImageFormatPreferenceTestCase(
    BaseImagingTestCase
):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.AUTO_WEBP = True
        cfg.AUTO_AVIF = True
        cfg.AUTO_IMAGE_FORMAT_PREFERENCE = ""

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        ctx = Context(server, cfg, importer)
        ctx.server.gifsicle_path = which("gifsicle")
        return ctx

    async def get_as_webp_first(self, url):
        return await self.async_fetch(
            url, headers={"Accept": "image/webp,image/avif,*/*;q=0.8"}
        )

    @gen_test
    async def test_can_auto_convert_to_webp(self):
        response = await self.get_as_webp_first("/unsafe/image.jpg")
        expect(response.code).to_equal(200)
        expect(response.headers).to_include("Vary")
        expect(response.headers["Vary"]).to_include("Accept")

        expect(response.body).to_be_webp()
