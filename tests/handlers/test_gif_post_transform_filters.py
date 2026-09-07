# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from io import BytesIO
from pathlib import Path
from shutil import rmtree, which
from tempfile import mkdtemp

from PIL import Image, ImageSequence
from tornado.testing import gen_test

from tests.base import TestCase
from thumbor.config import Config
from thumbor.context import ServerParameters


class GifPostTransformFiltersTestCase(TestCase):
    colors = [(0, 51, 102), (51, 102, 0), (102, 0, 51)]

    def setUp(self):
        self.loader_path = Path(mkdtemp())
        self.addCleanup(rmtree, self.loader_path)
        frames = [Image.new("RGB", (16, 8), color) for color in self.colors]
        frames[0].save(self.loader_path / "static.gif")
        frames[0].save(self.loader_path / "static.png")
        frames[0].save(
            self.loader_path / "animated.gif",
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0,
        )
        super().setUp()

    def get_config(self):
        return Config(
            SECURITY_KEY="ACME-SEC",
            LOADER="thumbor.loaders.file_loader",
            FILE_LOADER_ROOT_PATH=str(self.loader_path),
            STORAGE="thumbor.storages.no_storage",
            RESULT_STORAGE="thumbor.result_storages.no_storage",
        )

    def get_server(self):
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.gifsicle_path = which("gifsicle")
        return server

    @gen_test
    async def test_brightness_filters_static_and_animated_gifs(self):
        for use_gifsicle in (False, None, True):
            self.config.USE_GIFSICLE_ENGINE = use_gifsicle
            for filename in ("static.gif", "animated.gif", "static.png"):
                with self.subTest(engine=use_gifsicle, source=filename):
                    response = await self.async_fetch(
                        f"/unsafe/filters:brightness(50)/{filename}"
                    )
                    assert response.code == 200
                    colors = (
                        self.colors
                        if filename == "animated.gif"
                        else self.colors[:1]
                    )
                    if not use_gifsicle or filename.endswith(".png"):
                        colors = [
                            tuple(channel + 127 for channel in color)
                            for color in colors
                        ]
                    with Image.open(BytesIO(response.body)) as result:
                        assert result.n_frames == len(colors)
                        pixels = [
                            frame.convert("RGB").getpixel((0, 0))
                            for frame in ImageSequence.Iterator(result)
                        ]
                        assert pixels == colors

    @gen_test
    async def test_grayscale_filters_static_gifs(self):
        for use_gifsicle in (False, None, True):
            self.config.USE_GIFSICLE_ENGINE = use_gifsicle
            for filename in ("static.gif", "static.png"):
                with self.subTest(engine=use_gifsicle, source=filename):
                    response = await self.async_fetch(
                        f"/unsafe/filters:grayscale()/{filename}"
                    )
                    assert response.code == 200
                    with Image.open(BytesIO(response.body)) as result:
                        pixel = result.convert("RGB").getpixel((0, 0))
                        if use_gifsicle and filename.endswith(".gif"):
                            assert pixel == self.colors[0]
                        else:
                            assert pixel[0] == pixel[1] == pixel[2]

    @gen_test
    async def test_upscale_filters_static_gifs(self):
        for use_gifsicle in (False, None, True):
            self.config.USE_GIFSICLE_ENGINE = use_gifsicle
            for filename in ("static.gif", "static.png"):
                with self.subTest(engine=use_gifsicle, source=filename):
                    response = await self.async_fetch(
                        f"/unsafe/fit-in/48x24/filters:upscale()/{filename}"
                    )
                    assert response.code == 200
                    with Image.open(BytesIO(response.body)) as result:
                        if use_gifsicle and filename.endswith(".gif"):
                            assert result.size == (16, 8)
                        else:
                            assert result.size == (48, 24)
