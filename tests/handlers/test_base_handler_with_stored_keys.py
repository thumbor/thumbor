#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect
from tornado.testing import gen_test

from tests.fixtures.images import default_image
from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.importer import Importer


class ImageOperationsWithStoredKeysTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="MYKEY")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.ALLOW_UNSAFE_URL = False
        cfg.STORES_CRYPTO_KEY_FOR_EACH_IMAGE = True

        cfg.STORAGE = "thumbor.storages.file_storage"
        cfg.STORAGE_FILE_STORAGE_ROOT_PATH = self.root_path

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8891, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "MYKEY"
        return Context(server, cfg, importer)

    @gen_test
    async def test_stored_security_key_with_regular_image(self):
        storage = self.context.modules.storage
        self.context.server.security_key = "MYKEY"
        await storage.put_crypto(
            "image.jpg"
        )  # Write a file on the file storage containing the security key
        self.context.server.security_key = "MYKEY2"

        try:
            response = await self.async_fetch(
                "/nty7gpBIRJ3GWtYDLLw6q1PgqTo=/smart/image.jpg"
            )
            expect(response.code).to_equal(200)
            expect(response.body).to_be_similar_to(default_image())
        finally:
            self.context.server.security_key = "MYKEY"

    @gen_test
    async def test_stored_security_key_with_regular_image_with_querystring(
        self,
    ):  # NOQA
        storage = self.context.modules.storage
        self.context.server.security_key = "MYKEY"
        await storage.put_crypto(
            "image.jpg%3Fts%3D1"
        )  # Write a file on the file storage containing the security key
        self.context.server.security_key = "MYKEY2"

        response = await self.async_fetch(
            "/Iw7LZGdr-hHj2gQ4ZzksP3llQHY=/smart/image.jpg%3Fts%3D1"
        )
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(default_image())

    @gen_test
    async def test_stored_security_key_with_regular_image_with_hash(self):
        storage = self.context.modules.storage
        self.context.server.security_key = "MYKEY"
        await storage.put_crypto(
            "image.jpg%23something"
        )  # Write a file on the file storage containing the security key
        self.context.server.security_key = "MYKEY2"

        response = await self.async_fetch(
            "/fxOHtHcTZMyuAQ1YPKh9KWg7nO8=/smart/image.jpg%23something"
        )
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(default_image())
