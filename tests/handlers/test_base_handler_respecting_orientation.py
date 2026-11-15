# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from io import BytesIO
from os.path import join
from shutil import which

from PIL import Image
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
        assert response.code == 200
        engine = Engine(self.context)
        engine.load(response.body, ".jpg")
        assert engine.size == (4052, 3456)

    @gen_test
    async def test_no_upscale_limits_to_oriented_size(self):
        for dimensions in ("1000x1000", "origx1000"):
            response = await self.async_fetch(
                f"/unsafe/{dimensions}/filters:no_upscale()/"
                "Giunchedi%2C_Filippo_January_2015_01-"
                "cmyk-orientation-exif.jpg"
            )

            assert response.code == 200

            engine = Engine(self.context)
            engine.load(response.body, ".jpg")

            assert engine.size == (533, 800)

    @gen_test
    async def test_should_be_ok_without_orientation_exif(self):
        response = await self.async_fetch("/unsafe/20x20.jpg")
        assert response.code == 200
        engine = Engine(self.context)
        engine.load(response.body, ".jpg")
        assert engine.size == (20, 20)


class WebpSourceWithRespectOrientation(BaseImagingTestCase):
    def get_context(self):
        exif = Image.Exif()
        exif[274] = 6
        exif[271] = "thumbor"
        image = Image.new("RGB", (60, 40), "red")
        image.save(join(self.root_path, "sideways.webp"), exif=exif.tobytes())

        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.root_path
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.RESPECT_ORIENTATION = True
        cfg.PRESERVE_EXIF_INFO = True

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"

        return Context(server, cfg, importer)

    @gen_test
    async def test_should_rotate_a_webp_by_its_exif(self):
        for image_format in ("webp", "jpeg"):
            with self.assertNoLogs("thumbor", "ERROR"):
                response = await self.async_fetch(
                    f"/unsafe/filters:format({image_format})/sideways.webp"
                )

            assert response.code == 200

            with Image.open(BytesIO(response.body)) as image:
                assert image.size == (40, 60)
                assert image.getexif()[271] == "thumbor"
                assert image.getexif()[274] == 1
