# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2022 globo.com thumbor@googlegroups.com

from preggy import expect
from tornado.testing import gen_test

from PIL import Image

from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.engines.pil import Engine
from thumbor.importer import Importer
from thumbor.testing import get_ssim


class TestCrop(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.no_storage"

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        self.context = Context(server, cfg, importer)
        return self.context

    @gen_test
    async def test_crop_ssim(self):
        response = await self.async_fetch("/unsafe/180x180/icon-orig.png")
        engine = Engine(self.context)
        engine.load(response.body, ".png")
        image = Image.open(engine)
        expected = Image.open("./tests/fixtures/images/icon-expected.png")
        ssim = get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.97)
