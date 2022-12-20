# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2022, globo.com <thumbor@g.globo>

from io import BytesIO

from PIL import Image
from preggy import expect
from tornado.testing import gen_test

from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.engines.pil import Engine
from thumbor.importer import Importer

# pylint: disable=broad-except,abstract-method,attribute-defined-outside-init,line-too-long,too-many-public-methods
# pylint: disable=too-many-lines


class ImageOperationsWithKeepExifCopyrightTags(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.RESPECT_ORIENTATION = True

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        self.context = Context(server, cfg, importer)
        return self.context

    @gen_test
    async def test_should_not_return_exif_copyright_tags_with_copyright_tags(
        self,
    ):
        self.context.config.PRESERVE_EXIF_COPYRIGHT_INFO = False
        self.context.config.PRESERVE_EXIF_INFO = False
        response = await self.async_fetch(
            "/unsafe/filters:strip_exif()/thumbor-exif.png"
        )
        expect(response.code).to_equal(200)
        ctx = self.context
        engine = Engine(ctx)
        engine.load(response.body, ".jpg")
        final_bytes = BytesIO(engine.read())
        image = Image.open(final_bytes)
        expect(image.info.get("exif")).to_be_null()

    @gen_test
    async def test_should_return_exif_copyright_tags(self):
        self.context.config.PRESERVE_EXIF_COPYRIGHT_INFO = True
        response = await self.async_fetch(
            "/unsafe/filters:strip_exif()/thumbor-exif.png"
        )
        expect(response.code).to_equal(200)

        engine = Engine(self.context)
        engine.load(response.body, ".jpg")
        final_bytes = BytesIO(engine.read())
        image = Image.open(final_bytes)
        expect(image.info.get("exif")).not_to_be_null()

    @gen_test
    async def test_should_not_return_exif_copyright_tags(self):
        self.context.config.PRESERVE_EXIF_COPYRIGHT_INFO = True
        response = await self.async_fetch("/unsafe/20x20.jpg")
        expect(response.code).to_equal(200)
        engine = Engine(self.context)
        engine.load(response.body, ".jpg")
        final_bytes = BytesIO(engine.read())
        image = Image.open(final_bytes)

        expect(image.info.get("exif")).to_be_null()
