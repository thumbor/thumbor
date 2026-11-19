# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

from unittest import mock

from PIL import Image
from tornado.testing import gen_test

from tests.fixtures.images import get_abs_path, get_image, valid_image
from tests.handlers.test_upload_api import UploadTestCase
from thumbor.config import Config
from thumbor.context import Context
from thumbor.importer import Importer


class UploadAPIPixelLimitTestCase(UploadTestCase):
    def setUp(self):
        self.max_pixels = Image.MAX_IMAGE_PIXELS
        super().setUp()

    def tearDown(self):
        super().tearDown()
        Image.MAX_IMAGE_PIXELS = self.max_pixels

    def get_context(self):
        cfg = Config()
        cfg.UPLOAD_ENABLED = True
        cfg.UPLOAD_PHOTO_STORAGE = "thumbor.storages.file_storage"
        cfg.FILE_STORAGE_ROOT_PATH = self.root_path
        cfg.MAX_PIXELS = 1000

        importer = Importer(cfg)
        importer.import_modules()

        return Context(None, cfg, importer)

    @gen_test
    async def test_posting_an_image_over_the_pixel_limit_fails(self):
        response = await self.async_post(
            self.base_uri, {"Content-Type": "image/jpeg"}, valid_image()
        )

        assert response.code == 415

    @gen_test
    async def test_posting_jxl_over_the_pixel_limit_fails(self):
        with mock.patch.object(Image, "open") as image_open:
            response = await self.async_post(
                self.base_uri,
                {"Content-Type": "image/jxl"},
                get_image(get_abs_path("image.jxl")),
            )

        assert response.code == 415
        image_open.assert_not_called()
