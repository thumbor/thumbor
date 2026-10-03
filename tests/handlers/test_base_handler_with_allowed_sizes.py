# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

from libthumbor import CryptoURL
from tornado.testing import gen_test

from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.engines.pil import Engine
from thumbor.importer import Importer


class ImageOperationsWithAllowedSizesTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.ALLOWED_SIZES = ["200x100", "300x0", "origx100"]

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    def get_size(self, body):
        engine = Engine(self.context)
        engine.load(body, ".jpg")
        return engine.size

    @gen_test
    async def test_should_serve_allowed_size(self):
        response = await self.async_fetch("/unsafe/200x100/image.jpg")

        assert response.code == 200
        assert self.get_size(response.body) == (200, 100)

    @gen_test
    async def test_should_reject_size_not_allowed(self):
        response = await self.async_fetch("/unsafe/200x101/image.jpg")

        assert response.code == 400

    @gen_test
    async def test_should_reject_width_and_height_of_different_entries(self):
        response = await self.async_fetch("/unsafe/300x100/image.jpg")

        assert response.code == 400

    @gen_test
    async def test_should_reject_url_without_size(self):
        response = await self.async_fetch("/unsafe/image.jpg")

        assert response.code == 400

    @gen_test
    async def test_should_compare_omitted_dimension_as_zero(self):
        for url in ("/unsafe/300x0/image.jpg", "/unsafe/300x/image.jpg"):
            response = await self.async_fetch(url)

            assert response.code == 200, url

    @gen_test
    async def test_should_compare_dimensions_as_parsed_numbers(self):
        response = await self.async_fetch("/unsafe/0200x0100/image.jpg")

        assert response.code == 200

    @gen_test
    async def test_should_compare_orig_literally(self):
        response = await self.async_fetch("/unsafe/origx100/image.jpg")

        assert response.code == 200

    @gen_test
    async def test_should_ignore_flips_and_fit_in(self):
        for url in (
            "/unsafe/-200x-100/image.jpg",
            "/unsafe/fit-in/200x100/image.jpg",
            "/unsafe/adaptive-full-fit-in/200x100/image.jpg",
        ):
            response = await self.async_fetch(url)

            assert response.code == 200, url

    @gen_test
    async def test_should_reject_before_loading_the_image(self):
        allowed = await self.async_fetch("/unsafe/200x100/missing.jpg")
        rejected = await self.async_fetch("/unsafe/200x101/missing.jpg")

        assert allowed.code == 404
        assert rejected.code == 400

    @gen_test
    async def test_should_check_signed_urls(self):
        crypto = CryptoURL("ACME-SEC")
        allowed = crypto.generate(width=200, height=100, image_url="image.jpg")
        rejected = crypto.generate(
            width=200, height=101, image_url="image.jpg"
        )

        assert (await self.async_fetch(allowed)).code == 200
        assert (await self.async_fetch(rejected)).code == 400
