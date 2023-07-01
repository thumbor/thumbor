#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import json
import os
from os.path import dirname
from shutil import which
from unittest.mock import Mock, patch

from preggy import expect
from tornado.testing import gen_test

from tests.fixtures.images import animated_image
from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.importer import Importer
from thumbor.result_storages.file_storage import Storage as FileResultStorage

JPEGTRAN_AVAILABLE = which("jpegtran") is not None
EXIFTOOL_AVAILABLE = which("exiftool") is not None


class ImageOperationsWithResultStorageTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path

        cfg.RESULT_STORAGE = "thumbor.result_storages.file_storage"
        cfg.RESULT_STORAGE_EXPIRATION_SECONDS = 60
        cfg.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = self.root_path

        cfg.USE_GIFSICLE_ENGINE = True
        cfg.FFMPEG_PATH = which("ffmpeg")
        cfg.AUTO_WEBP = True
        cfg.OPTIMIZERS = [
            "thumbor.optimizers.gifv",
        ]

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        ctx = Context(server, cfg, importer)
        ctx.server.gifsicle_path = which("gifsicle")

        return ctx

    @property
    def result_storage(self):
        return self.context.modules.result_storage

    @patch("tornado.ioloop.IOLoop.instance")
    @gen_test
    async def test_saves_image_to_result_storage(self, instance_mock):
        instance_mock.return_value = self.io_loop
        response = await self.async_fetch(
            "/gTr2Xr9lbzIa2CT_dL_O0GByeR0=/animated.gif"
        )
        expect(response.code).to_equal(200)

        self.context.request = Mock(
            accepts_webp=False,
        )
        expected_path = self.result_storage.normalize_path(
            "/gTr2Xr9lbzIa2CT_dL_O0GByeR0=/animated.gif"
        )
        expect(expected_path).to_exist()
        expect(response.body).to_be_similar_to(animated_image())

    @patch("tornado.ioloop.IOLoop.instance")
    @gen_test
    async def test_saves_meta_to_result_storage(self, instance_mock):
        instance_mock.return_value = self.io_loop
        response = await self.async_fetch(
            "/oGi9XL4nHJKGEKVHjHEp1Jg1KpM=/meta/animated.gif"
        )
        expect(response.code).to_equal(200)

        self.context.request = Mock(
            accepts_webp=False,
        )
        expected_path = self.result_storage.normalize_path(
            "/oGi9XL4nHJKGEKVHjHEp1Jg1KpM=/meta/animated.gif"
        )
        expect(expected_path).to_exist()

        expected_source = {
            "frameCount": 2,
            "height": 100,
            "url": "animated.gif",
            "width": 100,
        }
        metadata = json.loads(response.body)
        expect(metadata).to_include("thumbor")
        expect(metadata["thumbor"]).to_include("source")
        expect(metadata["thumbor"]["source"]).to_be_like(expected_source)


class ImageOperationsResultStorageOnlyTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = "/path/that/does/not/exist"

        cfg.RESULT_STORAGE = "thumbor.result_storages.file_storage"
        cfg.RESULT_STORAGE_EXPIRATION_SECONDS = 60
        cfg.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = self.root_path
        cfg.FFMPEG_PATH = which("ffmpeg")

        cfg.USE_GIFSICLE_ENGINE = True
        cfg.AUTO_WEBP = True
        cfg.OPTIMIZERS = [
            "thumbor.optimizers.gifv",
        ]

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        ctx = Context(server, cfg, importer)
        ctx.server.gifsicle_path = which("gifsicle")

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
            "gTr2Xr9lbzIa2CT_dL_O0GByeR0=/animated.gif"
        )
        os.makedirs(dirname(expected_path))
        with open(expected_path, "wb") as img:
            img.write(animated_image())

        response = await self.async_fetch(
            "/gTr2Xr9lbzIa2CT_dL_O0GByeR0=/animated.gif"
        )
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(animated_image())

    @patch.object(FileResultStorage, "get", side_effect=Exception)
    @gen_test
    async def test_loads_image_from_result_storage_fails_on_exception(self, _):
        response = await self.async_fetch(
            "/gTr2Xr9lbzIa2CT_dL_O0GByeR0=/animated.gif"
        )
        expect(response.code).to_equal(500)
        expect(response.body).to_be_empty()
