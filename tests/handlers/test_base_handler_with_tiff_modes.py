# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

import struct
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
        Image.frombytes(
            "I;16", (3, 1), struct.pack("<3H", 0x2000, 0xFEFF, 0xFFFF)
        ).save(join(loader_path, "gray16.tif"))
        Image.frombytes(
            "I;16B", (3, 1), struct.pack(">3H", 0x2000, 0xFEFF, 0xFFFF)
        ).save(join(loader_path, "gray16be.tif"))

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

    @gen_test
    async def test_serves_16bit_gray_tiff_as_16bit_png(self):
        response = await self.async_fetch("/unsafe/gray16.tif")

        assert response.code == 200
        assert response.headers["Content-Type"] == "image/png"
        image = Image.open(BytesIO(response.body))
        assert image.mode == "I;16"
        assert [image.getpixel((x, 0)) for x in range(3)] == [
            0x2000,
            0xFEFF,
            0xFFFF,
        ]

    @gen_test
    async def test_scales_16bit_gray_tiff_down_for_an_8bit_format(self):
        response = await self.async_fetch(
            "/unsafe/filters:format(gif)/gray16.tif"
        )

        assert response.code == 200
        assert response.headers["Content-Type"] == "image/gif"
        image = Image.open(BytesIO(response.body)).convert("L")
        assert [image.getpixel((x, 0)) for x in range(3)] == [
            0x20,
            0xFE,
            0xFF,
        ]

    @gen_test
    async def test_scales_16bit_gray_tiff_down_for_a_filter(self):
        response = await self.async_fetch(
            "/unsafe/filters:brightness(0)/gray16.tif"
        )

        assert response.code == 200
        assert response.headers["Content-Type"] == "image/png"
        image = Image.open(BytesIO(response.body))
        assert image.mode == "RGB"
        assert [image.getpixel((x, 0)) for x in range(3)] == [
            (0x20, 0x20, 0x20),
            (0xFE, 0xFE, 0xFE),
            (0xFF, 0xFF, 0xFF),
        ]

    @gen_test
    async def test_resizes_big_endian_16bit_gray_tiff_like_little_endian(self):
        little = await self.async_fetch("/unsafe/6x2/gray16.tif")
        big = await self.async_fetch("/unsafe/6x2/gray16be.tif")

        assert big.code == 200
        assert big.headers["Content-Type"] == "image/png"
        image = Image.open(BytesIO(big.body))
        assert image.mode == "I;16"
        assert image.size == (6, 2)
        assert image.tobytes() == Image.open(BytesIO(little.body)).tobytes()
