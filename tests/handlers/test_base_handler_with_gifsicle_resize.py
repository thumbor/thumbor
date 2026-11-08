# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

from io import BytesIO
from shutil import which

from PIL import Image
from tornado.testing import gen_test

from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.importer import Importer

# pylint: disable=abstract-method,attribute-defined-outside-init


class ImageOperationsWithGifsicleResizeTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.USE_GIFSICLE_ENGINE = True

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
    async def test_resizes_animated_gif_to_the_requested_size(self):
        for width, height in ((50, 70), (70, 50), (70, 70)):
            with self.subTest(size=(width, height)):
                response = await self.async_fetch(
                    f"/unsafe/{width}x{height}/animated.gif"
                )

                assert response.code == 200
                assert response.headers["Content-Type"] == "image/gif"
                image = Image.open(BytesIO(response.body))
                assert image.size == (width, height)
                assert image.n_frames == 2
