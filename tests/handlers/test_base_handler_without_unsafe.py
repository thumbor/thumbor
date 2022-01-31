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

# pylint: disable=broad-except,abstract-method,attribute-defined-outside-init,line-too-long,too-many-public-methods
# pylint: disable=too-many-lines


class ImageOperationsWithoutUnsafeTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.ALLOW_UNSAFE_URL = False

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8890, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    @gen_test
    async def test_can_get_image_with_signed_url(self):
        response = await self.async_fetch(
            "/_wIUeSaeHw8dricKG2MGhqu5thk=/smart/image.jpg"
        )
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(default_image())

    @gen_test
    async def test_getting_unsafe_image_fails(self):
        response = await self.async_fetch("/unsafe/smart/image.jpg")
        expect(response.code).to_equal(400)
