# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from tornado.testing import gen_test

from tests.base import TestCase
from thumbor.config import Config
from thumbor.context import Context
from thumbor.importer import Importer


class HealthcheckHandlerTestCase(TestCase):
    @gen_test
    async def test_can_get_healthcheck(self):
        response = await self.async_get("/healthcheck")
        assert response.code == 200
        assert response.body == b"WORKING"
        assert response.headers.get("Cache-Control") == "no-cache"

    @gen_test
    async def test_can_head_healthcheck(self):
        response = await self.async_fetch("/healthcheck", method="HEAD")
        assert response.code == 200
        assert response.headers.get("Cache-Control") == "no-cache"


# Same test, but configured for the root URL
class HealthcheckOnRootTestCase(TestCase):
    def get_context(self):
        cfg = Config()
        cfg.HEALTHCHECK_ROUTE = "/"

        importer = Importer(cfg)
        importer.import_modules()

        return Context(None, cfg, importer)

    @gen_test
    async def test_can_get_healthcheck(self):
        response = await self.async_get("/")
        assert response.code == 200
        assert response.body == b"WORKING"

    @gen_test
    async def test_can_head_healthcheck(self):
        response = await self.async_fetch("/", method="HEAD")
        assert response.code == 200
