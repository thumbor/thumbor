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
from unittest import mock

from PIL import Image, ImageSequence
from tornado.testing import gen_test

from tests.base import TestCase
from thumbor.config import Config
from thumbor.context import ServerParameters
from thumbor.engines.pil import Engine
from thumbor.loaders import file_loader


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
        transparent = [Image.new("RGBA", (16, 8)) for _ in self.colors]
        for frame, color in zip(transparent, self.colors):
            frame.paste(color + (255,), (4, 2, 12, 6))
        transparent[0].save(
            self.loader_path / "transparent.gif",
            save_all=True,
            append_images=transparent[1:],
            duration=100,
            loop=0,
            disposal=2,
        )
        Image.new("RGB", (4, 4), "white").save(
            self.loader_path / "watermark.png"
        )
        Image.new("RGBA", (4, 4), "white").save(self.loader_path / "frame.png")
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
    async def test_grayscale_filters_static_and_animated_gifs(self):
        for use_gifsicle in (False, None, True):
            self.config.USE_GIFSICLE_ENGINE = use_gifsicle
            for filename in ("static.gif", "animated.gif", "static.png"):
                with self.subTest(engine=use_gifsicle, source=filename):
                    response = await self.async_fetch(
                        f"/unsafe/filters:grayscale()/{filename}"
                    )
                    assert response.code == 200
                    colors = (
                        self.colors
                        if filename == "animated.gif"
                        else self.colors[:1]
                    )
                    with Image.open(BytesIO(response.body)) as result:
                        pixels = [
                            frame.convert("RGB").getpixel((0, 0))
                            for frame in ImageSequence.Iterator(result)
                        ]
                    assert len(pixels) == len(colors)
                    if use_gifsicle and filename.endswith(".gif"):
                        assert pixels == colors
                    else:
                        assert all(r == g == b for r, g, b in pixels)

    @gen_test
    async def test_grayscale_keeps_animated_gif_transparency(self):
        response = await self.async_fetch(
            "/unsafe/filters:grayscale()/transparent.gif"
        )
        assert response.code == 200
        with Image.open(BytesIO(response.body)) as result:
            frames = [
                frame.convert("RGBA")
                for frame in ImageSequence.Iterator(result)
            ]
        assert len(frames) == len(self.colors)
        for frame in frames:
            assert frame.getpixel((0, 0))[3] == 0
            red, green, blue, alpha = frame.getpixel((8, 4))
            assert red == green == blue
            assert alpha == 255

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

    @gen_test
    async def test_resize_filters_resize_every_animated_gif_frame(self):
        for path, size in (
            ("fit-in/48x24/filters:upscale()", (48, 24)),
            ("filters:proportion(0.5)", (8, 4)),
        ):
            with self.subTest(path=path):
                response = await self.async_fetch(
                    f"/unsafe/{path}/animated.gif"
                )
                assert response.code == 200
                with Image.open(BytesIO(response.body)) as result:
                    assert result.size == size
                    corner = (size[0] - 1, size[1] - 1)
                    pixels = [
                        frame.convert("RGB").getpixel(corner)
                        for frame in ImageSequence.Iterator(result)
                    ]
                    assert pixels == self.colors

    @gen_test
    async def test_jpeg_format_keeps_animated_gifs_animated(self):
        for filename, image_format, frames in (
            ("static.gif", "JPEG", 1),
            ("animated.gif", "GIF", 3),
        ):
            with self.subTest(source=filename):
                response = await self.async_fetch(
                    f"/unsafe/filters:format(jpeg)/{filename}"
                )
                assert response.code == 200
                with Image.open(BytesIO(response.body)) as result:
                    assert result.format == image_format
                    assert getattr(result, "n_frames", 1) == frames

    @gen_test
    async def test_watermark_loads_its_image_once_per_animation(self):
        with mock.patch.object(
            file_loader, "load", wraps=file_loader.load
        ) as load:
            response = await self.async_fetch(
                "/unsafe/filters:watermark(watermark.png,0,0,0)/animated.gif"
            )
        assert response.code == 200
        loaded = [call.args[1] for call in load.call_args_list]
        assert loaded.count("watermark.png") == 1
        with Image.open(BytesIO(response.body)) as result:
            pixels = [
                frame.convert("RGB").getpixel((0, 0))
                for frame in ImageSequence.Iterator(result)
            ]
        assert pixels == [(255, 255, 255)] * len(self.colors)

    @gen_test
    async def test_frame_loads_its_image_once_per_animation(self):
        with mock.patch.object(
            file_loader, "load", wraps=file_loader.load
        ) as load:
            response = await self.async_fetch(
                "/unsafe/filters:frame(frame.png)/animated.gif"
            )
        assert response.code == 200
        loaded = [call.args[1] for call in load.call_args_list]
        assert loaded.count("frame.png") == 1
        with Image.open(BytesIO(response.body)) as result:
            assert result.n_frames == len(self.colors)

    @gen_test
    async def test_canvas_filters_keep_animated_gif_frame_durations(self):
        durations = [100, 200, 6010]
        frames = [Image.new("RGB", (16, 8), color) for color in self.colors]
        frames[0].save(
            self.loader_path / "timed.gif",
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0,
        )
        for path in (
            "fit-in/8x8/filters:fill(blue)",
            "filters:background_color(blue)",
            "filters:frame(frame.png)",
        ):
            with self.subTest(path=path):
                response = await self.async_fetch(f"/unsafe/{path}/timed.gif")
                assert response.code == 200
                with Image.open(BytesIO(response.body)) as result:
                    assert [
                        frame.info.get("duration")
                        for frame in ImageSequence.Iterator(result)
                    ] == durations

    @gen_test
    async def test_max_bytes_stops_when_animation_ignores_quality(self):
        with mock.patch.object(
            Engine,
            "read_multiple",
            autospec=True,
            side_effect=Engine.read_multiple,
        ) as read_multiple:
            response = await self.async_fetch(
                "/unsafe/filters:format(webp):max_bytes(1)/animated.gif"
            )
        assert response.code == 200
        assert read_multiple.call_count == 2
        with Image.open(BytesIO(response.body)) as result:
            assert result.format == "WEBP"
            assert result.n_frames == len(self.colors)
