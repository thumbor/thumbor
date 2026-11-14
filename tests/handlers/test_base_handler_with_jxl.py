# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

from io import BytesIO
from os import walk
from unittest import mock

from PIL import Image
from tornado.testing import gen_test

from tests.base import pillow_formats, skip_unless_jxl
from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.engines.pil import Engine
from thumbor.importer import Importer

ORIENTATION = 0x0112


def decode(buffer):
    image = Image.open(BytesIO(buffer))
    image.load()

    return image


class JxlTestCase(BaseImagingTestCase):
    settings = {}

    def setUp(self):
        self.max_pixels = Image.MAX_IMAGE_PIXELS
        super().setUp()

    def tearDown(self):
        super().tearDown()
        Image.MAX_IMAGE_PIXELS = self.max_pixels

    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC", **self.settings)
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = self.root_path

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"

        return Context(server, cfg, importer)


class ImageOperationsWithJxlTestCase(JxlTestCase):
    @skip_unless_jxl
    @gen_test
    async def test_can_read_jxl(self):
        for name in ("image.jxl", "image-container.jxl"):
            response = await self.async_fetch(f"/unsafe/{name}")

            assert response.code == 200
            assert response.headers["Content-Type"] == "image/jxl"

            image = decode(response.body)

            assert image.format == "JXL"
            assert image.size == (300, 400)

    @skip_unless_jxl
    @gen_test
    async def test_can_resize_jxl_keeping_its_alpha(self):
        response = await self.async_fetch("/unsafe/50x0/image-alpha.jxl")

        assert response.code == 200

        image = decode(response.body)

        assert image.format == "JXL"
        assert image.mode == "RGBA"
        assert image.size == (50, 38)

    @skip_unless_jxl
    @gen_test
    async def test_jxl_format(self):
        response = await self.async_fetch(
            "/unsafe/filters:format(jxl)/image.jpg"
        )

        assert response.code == 200
        assert response.headers["Content-Type"] == "image/jxl"
        assert decode(response.body).format == "JXL"

    @skip_unless_jxl
    @gen_test
    async def test_can_convert_jxl_to_another_format(self):
        response = await self.async_fetch(
            "/unsafe/filters:format(png)/image-alpha.jxl"
        )

        assert response.code == 200
        assert response.headers["Content-Type"] == "image/png"

        image = decode(response.body)

        assert image.format == "PNG"
        assert image.mode == "RGBA"

    @skip_unless_jxl
    @gen_test
    async def test_jxl_quality_setting(self):
        self.context.config.QUALITY = 80
        self.context.config.JXL_QUALITY = 50

        with mock.patch.object(
            Engine,
            "read",
            autospec=True,
            side_effect=Engine.read,
        ) as mock_read:
            response = await self.async_fetch(
                "/unsafe/filters:format(jxl)/image.jpg"
            )

        assert response.code == 200
        mock_read.assert_called_with(mock.ANY, ".jxl", 50)

    @skip_unless_jxl
    @gen_test
    async def test_jxl_uses_the_general_quality_by_default(self):
        self.context.config.QUALITY = 80

        with mock.patch.object(
            Engine,
            "read",
            autospec=True,
            side_effect=Engine.read,
        ) as mock_read:
            response = await self.async_fetch(
                "/unsafe/filters:format(jxl)/image.jpg"
            )

        assert response.code == 200
        mock_read.assert_called_with(mock.ANY, ".jxl", 80)

    @skip_unless_jxl
    @gen_test
    async def test_animated_gif_does_not_become_jxl(self):
        response = await self.async_fetch(
            "/unsafe/filters:format(jxl)/animated.gif"
        )

        assert response.code == 200
        assert response.headers["Content-Type"] == "image/gif"

    @skip_unless_jxl
    @gen_test
    async def test_can_read_a_recompressed_jpeg(self):
        response = await self.async_fetch(
            "/unsafe/image-jpeg-recompressed.jxl"
        )

        assert response.code == 200
        assert decode(response.body).size == (300, 400)

    @skip_unless_jxl
    @gen_test
    async def test_truncated_jxl_is_a_bad_request(self):
        response = await self.async_fetch("/unsafe/image-truncated.jxl")

        assert response.code == 400

    @gen_test
    async def test_animated_jxl_is_a_bad_request(self):
        with mock.patch.object(Image, "open") as image_open:
            response = await self.async_fetch("/unsafe/animated.jxl")

        assert response.code == 400
        image_open.assert_not_called()

    @gen_test
    async def test_jxl_without_a_decoder_is_a_bad_request(self):
        with pillow_formats():
            response = await self.async_fetch("/unsafe/image.jxl")

        assert response.code == 400

    @gen_test
    async def test_jxl_format_without_an_encoder_keeps_the_source_format(
        self,
    ):
        with pillow_formats():
            response = await self.async_fetch(
                "/unsafe/filters:format(jxl)/image.jpg"
            )

        assert response.code == 200
        assert response.headers["Content-Type"] == "image/jpeg"
        assert decode(response.body).format == "JPEG"

    @gen_test
    async def test_jxl_quality_is_not_used_without_an_encoder(self):
        self.context.config.QUALITY = 80
        self.context.config.JXL_QUALITY = 50

        with (
            pillow_formats(),
            mock.patch.object(
                Engine,
                "read",
                autospec=True,
                side_effect=Engine.read,
            ) as mock_read,
        ):
            response = await self.async_fetch(
                "/unsafe/filters:format(jxl)/image.jpg"
            )

        assert response.code == 200
        mock_read.assert_called_with(mock.ANY, ".jxl", 80)

    @skip_unless_jxl
    @gen_test
    async def test_meta_reports_a_jxl_source(self):
        self.context.config.JXL_QUALITY = 50
        response = await self.async_fetch("/unsafe/meta/150x0/image.jxl")

        assert response.code == 200
        assert b'"width": 150' in response.body


class JxlOverThePixelLimitTestCase(JxlTestCase):
    settings = {"MAX_PIXELS": 300 * 400 - 1}

    @gen_test
    async def test_jxl_over_the_pixel_limit_is_a_bad_request(self):
        with mock.patch.object(Image, "open") as image_open:
            response = await self.async_fetch("/unsafe/image.jxl")

        assert response.code == 400
        image_open.assert_not_called()


class JxlOrientationTestCase(JxlTestCase):
    settings = {"PRESERVE_EXIF_INFO": True}

    async def assert_served_as_the_decoder_orients_it(self):
        for name in ("orientation-6-exif.jxl", "orientation-6-jpeg.jxl"):
            response = await self.async_fetch(
                f"/unsafe/filters:format(jpeg)/{name}"
            )

            assert response.code == 200

            image = decode(response.body)

            assert image.size == (400, 300)
            assert image.getexif().get(ORIENTATION, 1) == 1

    @skip_unless_jxl
    @gen_test
    async def test_keeps_the_pixels_the_decoder_rotated(self):
        self.context.config.RESPECT_ORIENTATION = False

        await self.assert_served_as_the_decoder_orients_it()

    @skip_unless_jxl
    @gen_test
    async def test_does_not_rotate_them_again(self):
        self.context.config.RESPECT_ORIENTATION = True

        await self.assert_served_as_the_decoder_orients_it()

    @skip_unless_jxl
    @gen_test
    async def test_keeps_the_other_exif_tags(self):
        response = await self.async_fetch(
            "/unsafe/filters:format(jpeg)/orientation-6-exif.jxl"
        )

        assert decode(response.body).getexif()[0x010F] == "thumbor"


class JxlWithResultStorageTestCase(JxlTestCase):
    settings = {
        "RESULT_STORAGE": "thumbor.result_storages.file_storage",
        "RESULT_STORAGE_EXPIRATION_SECONDS": 60,
        "RESULT_STORAGE_STORES_UNSAFE": True,
    }

    @skip_unless_jxl
    @gen_test
    async def test_serves_a_stored_jxl_with_its_content_type(self):
        url = "/unsafe/filters:format(jxl)/image.jpg"
        first = await self.async_fetch(url)

        assert first.code == 200
        assert any(files for _, _, files in walk(self.root_path))

        with mock.patch.object(Engine, "read", side_effect=AssertionError):
            stored = await self.async_fetch(url)

        assert stored.code == 200
        assert stored.headers["Content-Type"] == "image/jxl"
        assert stored.body == first.body
