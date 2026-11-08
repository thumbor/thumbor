# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

from io import BytesIO
from os import makedirs
from os.path import join

from PIL import Image
from tornado.testing import gen_test

from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.importer import Importer

# pylint: disable=abstract-method,attribute-defined-outside-init


class ImageOperationsWithTiffModesTestCase(BaseImagingTestCase):
    def get_context(self):
        loader_path = join(self.root_path, "sources")
        makedirs(loader_path)
        float_image = Image.new("F", (3, 1))
        float_image.putdata([-5.0, 100.5, 300.0])
        float_image.save(join(loader_path, "float.tif"))
        Image.new("CMYK", (1, 1), (0, 255, 255, 0)).save(
            join(loader_path, "cmyk.tif")
        )

        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = loader_path
        cfg.STORAGE = "thumbor.storages.file_storage"
        cfg.FILE_STORAGE_ROOT_PATH = join(self.root_path, "storage")

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    @gen_test
    async def test_serves_float_tiff_as_8bit_png(self):
        response = await self.async_fetch("/unsafe/float.tif")

        assert response.code == 200
        assert response.headers["Content-Type"] == "image/png"
        image = Image.open(BytesIO(response.body))
        assert image.mode == "L"
        assert [image.getpixel((x, 0)) for x in range(3)] == [0, 100, 255]

    @gen_test
    async def test_serves_cmyk_tiff_as_png(self):
        response = await self.async_fetch("/unsafe/cmyk.tif")

        assert response.code == 200
        assert response.headers["Content-Type"] == "image/png"
        image = Image.open(BytesIO(response.body))
        assert image.getpixel((0, 0)) == (255, 0, 0, 255)
