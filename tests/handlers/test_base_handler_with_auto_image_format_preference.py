# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2025 globo.com thumbor@googlegroups.com

from shutil import which
from types import SimpleNamespace
from unittest import mock

import pytest
from tornado.testing import gen_test

from tests.base import (
    assert_is_avif,
    assert_is_jpeg,
    assert_is_png,
    assert_is_webp,
)
from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.handlers import BaseHandler
from thumbor.importer import Importer


def resolve_preferred_extension(
    preference, accepted_formats=None, multiple=False, transparent=False
):
    accepted_formats = accepted_formats or set(preference)
    engine = mock.Mock(extension=".gif")
    engine.is_multiple.return_value = multiple
    engine.has_transparency.return_value = transparent
    engine.can_convert_to_webp.return_value = "webp" in accepted_formats
    engine.can_auto_convert_to_avif.return_value = "avif" in accepted_formats
    engine.can_auto_convert_to_heif.return_value = "heif" in accepted_formats
    engine.can_auto_convert_png_to_jpg.return_value = False
    request = SimpleNamespace(
        accepts_webp="webp" in accepted_formats,
        accepts_avif="avif" in accepted_formats,
        accepts_heif="heif" in accepted_formats,
        accepts_jpeg="jpg" in accepted_formats,
        accepts_png="png" in accepted_formats,
        auto_png_to_jpg=None,
        engine=engine,
    )
    context = SimpleNamespace(
        config=Config(AUTO_IMAGE_FORMAT_PREFERENCE=preference),
        request=request,
    )
    handler = object.__new__(BaseHandler)
    handler.context = context

    # pylint: disable=protected-access
    return handler._resolve_auto_image_extension(context)


@pytest.mark.parametrize(
    "image_format", ["webp", "avif", "jpg", "heif", "png"]
)
def test_resolves_every_supported_preferred_format(image_format):
    assert resolve_preferred_extension([image_format]) == f".{image_format}"


def test_skips_unsupported_preferred_format():
    assert (
        resolve_preferred_extension(
            ["avif", "webp"], accepted_formats={"webp"}
        )
        == ".webp"
    )


def test_skips_jpg_for_transparent_image():
    assert resolve_preferred_extension(["jpg"], transparent=True) == ".gif"


def test_skips_preferred_formats_for_multiple_images():
    assert (
        resolve_preferred_extension(["webp", "png"], multiple=True) == ".gif"
    )


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
        cfg.AUTO_IMAGE_FORMAT_PREFERENCE = ["avif", "webp", "jpg", "png"]

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
        assert response.code == 200
        assert "Vary" in response.headers
        assert "Accept" in response.headers["Vary"]

        assert_is_avif(response.body)

    @gen_test
    async def test_skips_preferred_format_rejected_with_quality_zero(self):
        response = await self.async_fetch(
            "/unsafe/image.jpg",
            headers={"Accept": "image/avif;q=0,image/webp;q=0.8"},
        )

        assert response.code == 200
        assert "Accept" in response.headers["Vary"]
        assert_is_webp(response.body)

    @gen_test
    async def test_falls_back_to_engine_extension_when_no_match_exists(self):
        response = await self.async_fetch(
            "/unsafe/image.jpg", headers={"Accept": "image/tiff"}
        )
        assert response.code == 200
        assert "Vary" in response.headers
        assert "Accept" in response.headers["Vary"]

        assert_is_jpeg(response.body)


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
        cfg.AUTO_IMAGE_FORMAT_PREFERENCE = []

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
        assert response.code == 200
        assert "Vary" in response.headers
        assert "Accept" in response.headers["Vary"]

        assert_is_webp(response.body)


class ImageOperationsWithAutoImageFormatPreferenceOverrideTestCase(
    BaseImagingTestCase
):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.AUTO_WEBP = False
        cfg.AUTO_AVIF = False
        cfg.AUTO_JPG = False
        cfg.AUTO_PNG = False
        cfg.AUTO_HEIF = False
        cfg.AUTO_IMAGE_FORMAT_PREFERENCE = [" invalid ", " WebP ", "webp"]
        cfg.FILTERS = [*cfg.FILTERS, "thumbor.filters.autojpg"]

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
    async def test_preference_overrides_auto_flags(self):
        response = await self.async_fetch(
            "/unsafe/image.jpg", headers={"Accept": "image/webp,*/*;q=0.8"}
        )
        assert response.code == 200
        assert "Vary" in response.headers
        assert "Accept" in response.headers["Vary"]

        assert_is_webp(response.body)

    @gen_test
    async def test_autojpg_false_does_not_override_explicit_jpg_preference(
        self,
    ):
        self.context.config.AUTO_IMAGE_FORMAT_PREFERENCE = ["jpg"]

        response = await self.async_fetch(
            "/unsafe/filters:autojpg(false)/"
            "Giunchedi%2C_Filippo_January_2015_01.png",
            headers={"Accept": "image/jpeg"},
        )

        assert response.code == 200
        assert_is_jpeg(response.body)


class ImageOperationsWithPreferenceAndAutoPngToJpgTestCase(
    BaseImagingTestCase
):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.AUTO_PNG_TO_JPG = True
        cfg.AUTO_IMAGE_FORMAT_PREFERENCE = ["webp"]
        cfg.FILTERS = [*cfg.FILTERS, "thumbor.filters.autojpg"]

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
    async def test_preferred_format_wins_over_auto_png_to_jpg(self):
        response = await self.async_fetch(
            "/unsafe/Giunchedi%2C_Filippo_January_2015_01.png",
            headers={"Accept": "image/webp"},
        )

        assert response.code == 200
        assert_is_webp(response.body)

    @gen_test
    async def test_auto_png_to_jpg_is_fallback_after_preference(self):
        response = await self.async_fetch(
            "/unsafe/Giunchedi%2C_Filippo_January_2015_01.png",
            headers={"Accept": "image/png"},
        )

        assert response.code == 200
        assert_is_jpeg(response.body)

    @gen_test
    async def test_autojpg_false_disables_only_png_to_jpg_fallback(self):
        response = await self.async_fetch(
            "/unsafe/filters:autojpg(false)/"
            "Giunchedi%2C_Filippo_January_2015_01.png",
            headers={"Accept": "image/png"},
        )

        assert response.code == 200
        assert_is_png(response.body)

    @gen_test
    async def test_autojpg_true_keeps_png_to_jpg_fallback_enabled(self):
        response = await self.async_fetch(
            "/unsafe/filters:autojpg(true)/"
            "Giunchedi%2C_Filippo_January_2015_01.png",
            headers={"Accept": "image/png"},
        )

        assert response.code == 200
        assert_is_jpeg(response.body)
