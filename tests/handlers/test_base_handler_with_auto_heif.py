#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2022 globo.com thumbor@googlegroups.com

from shutil import which

from preggy import expect
from tornado.testing import gen_test

from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.importer import Importer

# pylint: disable=broad-except,abstract-method,attribute-defined-outside-init,line-too-long,too-many-public-methods
# pylint: disable=too-many-lines

MIMETYPE = "image/heif"


class ImageOperationsWithAutoHeifTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.AUTO_HEIF = True

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        ctx = Context(server, cfg, importer)
        ctx.server.gifsicle_path = which("gifsicle")
        return ctx

    async def get_as_heif(self, url):
        return await self.async_fetch(
            url, headers={"Accept": f"{MIMETYPE},*/*;q=0.8"}
        )

    @gen_test
    async def test_can_auto_convert_jpeg_to_heif(self):
        response = await self.get_as_heif("/unsafe/image.jpg")

        expect(response.code).to_equal(200)
        expect(response.headers["Content-type"]).to_equal(MIMETYPE)
        expect(response.body).to_be_heif()

    @gen_test
    async def test_can_auto_convert_avif_to_heif(self):
        response = await self.get_as_heif("/unsafe/image.avif")

        expect(response.code).to_equal(200)
        expect(response.headers["Content-type"]).to_equal(MIMETYPE)
        expect(response.body).to_be_heif()

    @gen_test
    async def test_should_not_convert_animated_gifs_to_heif(self):
        response = await self.get_as_heif("/unsafe/animated.gif")

        expect(response.code).to_equal(200)
        expect(response.body).to_be_gif()

    @gen_test
    async def test_should_convert_image_with_small_width_and_no_height_to_heif(
        self,
    ):
        response = await self.get_as_heif("/unsafe/0x0:1681x596/1x/image.jpg")

        expect(response.code).to_equal(200)
        expect(response.headers["Content-type"]).to_equal(MIMETYPE)
        expect(response.body).to_be_heif()

    @gen_test
    async def test_should_convert_monochromatic_jpeg_to_heif(self):
        response = await self.get_as_heif("/unsafe/grayscale.jpg")
        expect(response.code).to_equal(200)
        expect(response.headers["Content-type"]).to_equal(MIMETYPE)
        expect(response.body).to_be_heif()

    @gen_test
    async def test_should_convert_cmyk_jpeg_to_heif(self):
        response = await self.get_as_heif("/unsafe/cmyk.jpg")
        expect(response.code).to_equal(200)
        expect(response.headers["Content-type"]).to_equal(MIMETYPE)
        expect(response.body).to_be_heif()

    @gen_test
    async def test_shouldnt_convert_to_cmyk_to_heif_if_format_specified(self):
        response = await self.get_as_heif(
            "/unsafe/filters:format(png)/cmyk.jpg"
        )
        expect(response.code).to_equal(200)
        expect(response.body).to_be_png()

    @gen_test
    async def test_shouldnt_convert_cmyk_to_heif_if_gif(self):
        response = await self.get_as_heif(
            "/unsafe/filters:format(gif)/cmyk.jpg"
        )
        expect(response.code).to_equal(200)
        expect(response.body).to_be_gif()

    @gen_test
    async def test_shouldnt_convert_gif_to_heif_if_format_specified(self):
        response = await self.get_as_heif(
            "/unsafe/filters:format(gif)/image.jpg"
        )
        expect(response.code).to_equal(200)
        expect(response.body).to_be_gif()

    @gen_test
    async def test_should_convert_to_heif_if_format_invalid(self):
        response = await self.get_as_heif(
            "/unsafe/filters:format(asdf)/image.jpg"
        )
        expect(response.code).to_equal(200)
        expect(response.headers["Content-type"]).to_equal(MIMETYPE)
        expect(response.body).to_be_heif()
