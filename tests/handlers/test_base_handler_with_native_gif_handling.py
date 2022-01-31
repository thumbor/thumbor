#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import os
from os.path import dirname
from unittest.mock import Mock

from preggy import expect
from tornado.testing import gen_test

from tests.fixtures.images import not_so_animated_image
from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.importer import Importer


class ImageOperationsWithGifWithoutGifsicle(BaseImagingTestCase):
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

        return ctx

    @gen_test
    async def test_should_be_ok_with_single_frame_gif(self):
        response = await self.async_fetch(
            "/5Xr8gyuWE7jL_VB72K0wvzTMm2U=/animated-one-frame.gif"
        )

        expect(response.code).to_equal(200)
        expect(response.headers["Content-Type"]).to_equal("image/gif")
        expect(response.body).to_be_similar_to(not_so_animated_image())


class ImageOperationsWithGifWithoutGifsicleOnResultStorage(
    BaseImagingTestCase
):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = "/path/that/does/not/exist"

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

        return ctx

    @property
    def result_storage(self):
        return self.context.modules.result_storage

    @gen_test
    async def test_loads_image_from_result_storage(self):
        self.context.request = Mock(
            accepts_webp=False,
        )
        expected_path = self.result_storage.normalize_path(
            "5Xr8gyuWE7jL_VB72K0wvzTMm2U=/animated-one-frame.gif"
        )
        os.makedirs(dirname(expected_path))
        with open(expected_path, "wb") as img:
            img.write(not_so_animated_image())

        response = await self.async_fetch(
            "/5Xr8gyuWE7jL_VB72K0wvzTMm2U=/animated-one-frame.gif"
        )
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(not_so_animated_image())
