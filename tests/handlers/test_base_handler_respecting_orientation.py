#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from shutil import which

from preggy import expect
from tornado.testing import gen_test

from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.engines.pil import Engine
from thumbor.importer import Importer

# pylint: disable=broad-except,abstract-method,attribute-defined-outside-init,line-too-long,too-many-public-methods
# pylint: disable=too-many-lines


class ImageOperationsWithRespectOrientation(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.RESPECT_ORIENTATION = True
        cfg.PRESERVE_EXIF_INFO = True

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        self.context = Context(server, cfg, importer)
        self.context.server.gifsicle_path = which("gifsicle")
        return self.context

    @gen_test
    async def test_should_be_ok_when_orientation_exif(self):
        response = await self.async_fetch(
            "/unsafe/10_years_of_Wikipedia_by_Guillaume_Paumier.jpg"
        )
        expect(response.code).to_equal(200)
        engine = Engine(self.context)
        engine.load(response.body, ".jpg")
        expect(engine.size).to_equal((4052, 3456))

    @gen_test
    async def test_should_be_ok_without_orientation_exif(self):
        response = await self.async_fetch("/unsafe/20x20.jpg")
        expect(response.code).to_equal(200)
        engine = Engine(self.context)
        engine.load(response.body, ".jpg")
        expect(engine.size).to_equal((20, 20))
