#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import shutil
import tempfile
from os.path import abspath, dirname, join

from preggy import expect
from tornado.testing import gen_test

from tests.base import TestCase
from thumbor.config import Config
from thumbor.context import ServerParameters
from thumbor.importer import Importer
from thumbor.server import validate_config

# pylint: disable=broad-except,abstract-method,attribute-defined-outside-init,line-too-long,too-many-public-methods
# pylint: disable=too-many-lines


class ImageBadRequestDecompressionBomb(TestCase):
    def setUp(self):
        self.root_path = tempfile.mkdtemp()
        self.loader_path = abspath(
            join(dirname(__file__), "../fixtures/images/")
        )
        self.base_uri = "/image"
        super().setUp()

    def tearDown(self):
        shutil.rmtree(self.root_path)

    async def get_as_webp(self, url):
        return await self.async_fetch(
            url, headers={"Accept": "image/webp,*/*;q=0.8"}
        )

    def get_config(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.AUTO_WEBP = True
        return cfg

    def get_server(self):
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        validate_config(self.config, server)
        return server

    def get_importer(self):
        importer = Importer(self.config)
        importer.import_modules()
        return importer

    @gen_test
    async def test_should_bad_request_if_bigger_than_75_megapixels(self):
        response = await self.get_as_webp("/unsafe/16384x16384.png")
        expect(response.code).to_equal(400)

    @gen_test
    async def test_should_bad_request_if_bigger_than_75_megapixels_jpeg(self):
        response = await self.get_as_webp("/unsafe/9643x10328.jpg")
        expect(response.code).to_equal(400)
