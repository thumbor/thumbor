#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from json import loads
from shutil import which

from preggy import expect
from tornado.testing import gen_test

from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.engines.pil import Engine
from thumbor.importer import Importer
from thumbor.storages.file_storage import Storage as FileStorage
from thumbor.storages.no_storage import Storage as NoStorage

# pylint: disable=broad-except,abstract-method,attribute-defined-outside-init,line-too-long,too-many-public-methods
# pylint: disable=too-many-lines


class StorageOverrideTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.file_storage"
        cfg.FILE_STORAGE_ROOT_PATH = self.root_path

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    @gen_test
    async def test_shouldnt_call_put_when_storage_overridden_to_nostorage(
        self,
    ):  # NOQA
        old_load = Engine.load
        old_put = FileStorage.put

        def load_override(self, arg, arg2):
            self.context.modules.storage = NoStorage(None)
            return old_load(self, arg, arg2)

        def put_override(*_):
            expect.not_to_be_here()

        Engine.load = load_override
        FileStorage.put = put_override

        response = await self.async_fetch("/unsafe/image.jpg")

        Engine.load = old_load
        FileStorage.put = old_put

        expect(response.code).to_equal(200)


class ImageOperationsWithoutStorage(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.AUTO_WEBP = True
        cfg.USE_GIFSICLE_ENGINE = True
        cfg.RESPECT_ORIENTATION = True

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        ctx = Context(server, cfg, importer)
        ctx.server.gifsicle_path = which("gifsicle")
        return ctx

    @gen_test
    async def test_meta(self):
        response = await self.async_fetch("/unsafe/meta/800x400/image.jpg")
        expect(response.code).to_equal(200)

    @gen_test
    async def test_meta_with_unicode(self):
        response = await self.async_fetch(
            "/unsafe/meta/200x300/alabama1_ap620%C3%A9.jpg"
        )
        expect(response.code).to_equal(200)
        obj = loads(response.body.decode("utf-8"))
        expect(obj["thumbor"]["target"]["width"]).to_equal(200)
        expect(obj["thumbor"]["target"]["height"]).to_equal(300)

    @gen_test
    async def test_meta_frame_count(self):
        response = await self.async_fetch("/unsafe/meta/800x400/image.jpg")
        expect(response.code).to_equal(200)
        obj = loads(response.body.decode("utf-8"))
        expect(obj["thumbor"]["source"]["frameCount"]).to_equal(1)

    @gen_test
    async def test_meta_frame_count_with_gif(self):
        response = await self.async_fetch("/unsafe/meta/animated.gif")
        expect(response.code).to_equal(200)
        obj = loads(response.body.decode("utf-8"))
        expect(obj["thumbor"]["source"]["frameCount"]).to_equal(2)

    @gen_test
    async def test_max_bytes(self):
        response = await self.async_fetch(
            "/unsafe/filters:max_bytes(35000)/Giunchedi%2C_"
            "Filippo_January_2015_01.jpg"
        )
        expect(response.code).to_equal(200)
        expect(len(response.body)).to_be_lesser_or_equal_to(35000)

    @gen_test
    async def test_max_bytes_impossible(self):
        response = await self.async_fetch(
            "/unsafe/filters:max_bytes(1000)/Giunchedi%2C_Filippo_"
            "January_2015_01.jpg"
        )
        expect(response.code).to_equal(200)
        expect(len(response.body)).to_be_greater_than(1000)

    @gen_test
    async def test_meta_with_exif_orientation(self):
        response = await self.async_fetch(
            "/unsafe/meta/0x0/Giunchedi%2C_Filippo_January_2015_01-"
            "cmyk-orientation-exif.jpg"
        )
        expect(response.code).to_equal(200)
        obj = loads(response.body.decode("utf-8"))
        expect(obj["thumbor"]["target"]["width"]).to_equal(533)
        expect(obj["thumbor"]["target"]["height"]).to_equal(800)
