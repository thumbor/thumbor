# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

import os
from shutil import which

from tornado.testing import gen_test

from tests.base import (
    assert_is_gif,
    assert_is_jpeg,
    assert_is_png,
    assert_is_webp,
)
from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.importer import Importer


class FormatFilterAllowedConversionsTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.RESULT_STORAGE = "thumbor.result_storages.file_storage"
        cfg.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = self.root_path
        cfg.RESULT_STORAGE_STORES_UNSAFE = True
        cfg.FORMAT_FILTER_ALLOWED_CONVERSIONS = {
            "jpg": ["jpg", "webp"],
            "svg": ["png"],
            "gif": ["gif"],
        }

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        server.gifsicle_path = which("gifsicle")
        return Context(server, cfg, importer)

    def count_stored_results(self):
        return sum(len(files) for _, _, files in os.walk(self.root_path))

    @gen_test
    async def test_should_serve_allowed_conversion(self):
        response = await self.async_fetch(
            "/unsafe/filters:format(webp)/image.jpg"
        )

        assert response.code == 200
        assert_is_webp(response.body)
        assert self.count_stored_results() == 1

    @gen_test
    async def test_should_reject_conversion_not_allowed(self):
        response = await self.async_fetch(
            "/unsafe/filters:format(png)/image.jpg"
        )

        assert response.code == 400
        assert self.count_stored_results() == 0

    @gen_test
    async def test_should_reject_when_any_format_call_is_not_allowed(self):
        response = await self.async_fetch(
            "/unsafe/filters:format(png):format(webp)/image.jpg"
        )

        assert response.code == 400

    @gen_test
    async def test_should_check_svg_by_its_detected_format(self):
        rejected = await self.async_fetch(
            "/unsafe/filters:format(webp)/Commons-logo.svg"
        )
        allowed = await self.async_fetch(
            "/unsafe/filters:format(png)/Commons-logo.svg"
        )

        assert rejected.code == 400
        assert allowed.code == 200
        assert_is_png(allowed.body)

    @gen_test
    async def test_should_check_animated_gifs(self):
        response = await self.async_fetch(
            "/unsafe/filters:format(png)/animated.gif"
        )

        assert response.code == 400

    @gen_test
    async def test_should_not_check_gifs_handled_by_gifsicle(self):
        self.context.config.USE_GIFSICLE_ENGINE = True

        response = await self.async_fetch(
            "/unsafe/filters:format(png)/animated.gif"
        )

        assert response.code == 200
        assert_is_gif(response.body)

    @gen_test
    async def test_should_check_meta_requests(self):
        response = await self.async_fetch(
            "/unsafe/meta/filters:format(png)/image.jpg"
        )

        assert response.code == 400

    @gen_test
    async def test_should_not_restrict_sources_not_listed(self):
        response = await self.async_fetch(
            "/unsafe/filters:format(webp)/256_color_palette.png"
        )

        assert response.code == 200
        assert_is_webp(response.body)

    @gen_test
    async def test_should_not_restrict_urls_without_format(self):
        response = await self.async_fetch("/unsafe/image.jpg")

        assert response.code == 200
        assert_is_jpeg(response.body)

    @gen_test
    async def test_should_not_restrict_auto_formats(self):
        self.context.config.AUTO_WEBP = True
        self.context.config.FORMAT_FILTER_ALLOWED_CONVERSIONS = {
            "jpg": ["jpg"]
        }

        response = await self.async_fetch(
            "/unsafe/image.jpg", headers={"Accept": "image/webp,*/*;q=0.8"}
        )

        assert response.code == 200
        assert_is_webp(response.body)

    @gen_test
    async def test_should_reject_conversion_accepted_by_auto_formats(self):
        self.context.config.AUTO_WEBP = True
        self.context.config.FORMAT_FILTER_ALLOWED_CONVERSIONS = {
            "jpg": ["jpg"]
        }

        response = await self.async_fetch(
            "/unsafe/filters:format(webp)/image.jpg",
            headers={"Accept": "image/webp,*/*;q=0.8"},
        )

        assert response.code == 400

    @gen_test
    async def test_should_prefer_allowed_format_over_auto_formats(self):
        self.context.config.AUTO_WEBP = True

        response = await self.async_fetch(
            "/unsafe/filters:format(jpg)/image.jpg",
            headers={"Accept": "image/webp,*/*;q=0.8"},
        )

        assert response.code == 200
        assert_is_jpeg(response.body)
        assert "Vary" not in response.headers

    @gen_test
    async def test_should_serve_stored_results_after_a_policy_change(self):
        url = "/unsafe/filters:format(webp)/image.jpg"
        await self.async_fetch(url)
        self.context.config.FORMAT_FILTER_ALLOWED_CONVERSIONS = {
            "jpg": ["jpg"]
        }

        response = await self.async_fetch(url)

        assert response.code == 200
        assert_is_webp(response.body)
