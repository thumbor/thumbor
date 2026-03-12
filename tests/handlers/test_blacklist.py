# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import tempfile
from os.path import abspath, dirname, join

from tornado.testing import gen_test

from tests.base import TestCase
from thumbor.config import Config
from thumbor.context import Context
from thumbor.importer import Importer


class BlacklistHandlerTestCase(TestCase):
    def get_context(self):
        file_storage_root_path = (
            tempfile.TemporaryDirectory().name  # pylint: disable=consider-using-with
        )
        cfg = Config()
        cfg.USE_BLACKLIST = True
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = abspath(
            join(dirname(__file__), "../fixtures/images/")
        )
        cfg.STORAGE = "thumbor.storages.file_storage"
        cfg.FILE_STORAGE_ROOT_PATH = file_storage_root_path
        importer = Importer(cfg)
        importer.import_modules()
        return Context(None, cfg, importer)

    @gen_test
    async def test_can_get_blacklist(self):
        response = await self.async_fetch("/blacklist")
        assert response.code == 200
        assert response.body == b""

    @gen_test
    async def test_can_put_object_to_blacklist(self):
        response = await self.async_fetch(
            "/blacklist?blocked.jpg", method="PUT", body=""
        )
        assert response.code == 200
        assert response.body == b""

    @gen_test
    async def test_can_read_updated_blacklist(self):
        await self.async_fetch("/blacklist?blocked.jpg", method="PUT", body="")
        response = await self.async_fetch("/blacklist")
        assert response.code == 200
        assert b"blocked.jpg\n" in response.body

    @gen_test
    async def test_cant_get_blacklisted_image(self):
        response = await self.async_fetch("/unsafe/image.jpg")
        assert response.code == 200
        await self.async_fetch("/blacklist?image.jpg", method="PUT", body="")
        response = await self.async_fetch("/unsafe/image.jpg")
        assert response.code == 400
