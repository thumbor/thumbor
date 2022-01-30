#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from shutil import which

from preggy import expect
from tornado.testing import gen_test

from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.engines.pil import Engine
from thumbor.importer import Importer

# pylint: disable=broad-except,abstract-method,attribute-defined-outside-init,line-too-long,too-many-public-methods
# pylint: disable=too-many-lines


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
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
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


class ImageOperationsWithMaxWidthAndMaxHeightShouldNotUpscale(
    BaseImagingTestCase
):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path

        cfg.MAX_WIDTH = 5000
        cfg.MAX_HEIGHT = 5000
        cfg.AUTO_WEBP = True
        cfg.MAX_AGE = 315360000
        cfg.ENGINE_THREADPOOL_SIZE = 2
        cfg.STORAGE = "thumbor.storages.no_storage"

        # Tried with optimizer on and off and made no difference
        cfg.OPTIMIZERS = [
            "thumbor.optimizers.jpegtran",
        ]

        cfg.RESULT_STORAGE = "thumbor.result_storages.no_storage"

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        ctx = Context(server, cfg, importer)

        return ctx

    @gen_test
    async def test_should_return_original_image_size(self):
        response = await self.async_fetch(
            "/unsafe/filters:format(jpeg)/very-small-jpeg.jpg"
        )

        engine = Engine(self.context)
        engine.load(response.body, ".jpg")
        expect(response.code).to_equal(200)
        expect(response.headers["Content-Type"]).to_equal("image/jpeg")
        expect(engine.size).to_equal((100, 100))

    @gen_test
    async def test_should_return_original_image_size_with_normalize(self):
        response = await self.async_fetch(
            "/unsafe/filters:format(jpeg)/weird_normalize_error.jpg"
        )

        engine = Engine(self.context)
        engine.load(response.body, ".jpg")
        expect(response.code).to_equal(200)
        expect(response.headers["Content-Type"]).to_equal("image/jpeg")
        expect(engine.size).to_equal((159, 239))


class ImageOperationsWithMaxPixels(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.MAX_PIXELS = 1000

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        ctx = Context(server, cfg, importer)
        ctx.server.gifsicle_path = which("gifsicle")
        return ctx

    @gen_test
    async def test_should_error(self):
        response = await self.async_fetch("/unsafe/200x200/grayscale.jpg")
        expect(response.code).to_equal(400)
