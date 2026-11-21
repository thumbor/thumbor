# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

from io import BytesIO
from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp
from unittest import mock

from PIL import GifImagePlugin, Image, ImageSequence
from tornado.testing import gen_test

from tests.base import AVIF_AVAILABLE, TestCase
from thumbor.config import Config
from thumbor.engines.pil import _gif_palette_frames

SCREEN = (60, 45)
RED, GREEN, BLUE = (255, 0, 0), (0, 255, 0), (0, 0, 255)
PALETTE = [0, 0, 0, *RED, *GREEN, *BLUE]


def three_frame_gif(
    transparent=False, first_size=SCREEN, second_offset=(30, 0)
):
    # Pillow only writes frames that fit the first one, so the blocks are
    # put together here. With the default offset the second frame starts
    # halfway across the logical screen and its right half falls outside
    frames = []
    for index, size in enumerate((first_size, SCREEN, SCREEN), start=1):
        frame = Image.new("P", size, 0 if transparent else index)
        frame.putpalette(PALETTE)
        frame.paste(index, (10, 10, 20, 20))
        frames.append(frame)
    options = {"duration": 100}
    if transparent:
        options.update(transparency=0, disposal=2)
    header, _ = GifImagePlugin.getheader(frames[0])
    blocks = list(header)
    blocks[0] = b"GIF89a" + bytes((SCREEN[0], 0, SCREEN[1], 0))
    for frame, offset in zip(frames, ((0, 0), second_offset, (0, 0))):
        blocks += GifImagePlugin.getdata(frame, offset, **options)
    return b"".join(blocks) + b";"


def decoded_frames(data):
    with Image.open(BytesIO(data)) as image:
        return [
            frame.convert("RGBA") for frame in ImageSequence.Iterator(image)
        ]


class GifFramesPastTheLogicalScreenTestCase(TestCase):
    def setUp(self):
        self.loader_path = Path(mkdtemp())
        self.addCleanup(rmtree, self.loader_path)
        for name, options in (
            ("opaque.gif", {}),
            ("transparent.gif", {"transparent": True}),
            ("large-first.gif", {"first_size": (80, 60)}),
        ):
            (self.loader_path / name).write_bytes(three_frame_gif(**options))
        Image.new("RGBA", (4, 4), "white").save(self.loader_path / "over.png")
        super().setUp()

    def get_config(self):
        return Config(
            SECURITY_KEY="ACME-SEC",
            LOADER="thumbor.loaders.file_loader",
            FILE_LOADER_ROOT_PATH=str(self.loader_path),
            STORAGE="thumbor.storages.no_storage",
            RESULT_STORAGE="thumbor.result_storages.no_storage",
        )

    def test_the_sources_decode_with_frames_of_different_sizes(self):
        for name, sizes in (
            ("opaque.gif", [(60, 45), (90, 45), (90, 45)]),
            ("transparent.gif", [(60, 45), (90, 45), (90, 45)]),
            ("large-first.gif", [(80, 60), (90, 60), (90, 60)]),
        ):
            with self.subTest(source=name):
                data = (self.loader_path / name).read_bytes()
                with Image.open(BytesIO(data)) as image:
                    assert [
                        frame.size for frame in ImageSequence.Iterator(image)
                    ] == sizes

    def test_pillow_10_loads_the_frames_with_its_default_strategy(self):
        default = GifImagePlugin.LOADING_STRATEGY
        palette = (
            GifImagePlugin.LoadingStrategy.RGB_AFTER_DIFFERENT_PALETTE_ONLY
        )
        for loses_frames, options, strategy in (
            (True, {"second_offset": (0, 0)}, palette),
            (True, {}, default),
            (True, {"first_size": (80, 60), "second_offset": (0, 0)}, default),
            (False, {}, palette),
        ):
            with (
                self.subTest(loses_frames=loses_frames, options=options),
                mock.patch(
                    "thumbor.engines.pil.PILLOW_LOSES_GROWN_GIF_FRAMES",
                    loses_frames,
                ),
                _gif_palette_frames(three_frame_gif(**options)),
            ):
                assert GifImagePlugin.LOADING_STRATEGY is strategy
            assert GifImagePlugin.LOADING_STRATEGY is default

    @gen_test
    async def test_later_frames_are_clipped_to_the_first_one(self):
        response = await self.async_fetch("/unsafe/transparent.gif")
        assert response.code == 200
        frames = decoded_frames(response.body)
        assert [frame.size for frame in frames] == [SCREEN] * 3
        assert [frame.info["duration"] for frame in frames] == [100] * 3
        for frame, color, visible, cleared in (
            (frames[0], RED, (15, 15), (45, 15)),
            (frames[1], GREEN, (45, 15), (15, 15)),
            (frames[2], BLUE, (15, 15), (45, 15)),
        ):
            assert frame.getpixel(visible) == color + (255,)
            assert frame.getpixel(cleared)[3] == 0

    @gen_test
    async def test_a_larger_first_frame_sets_the_canvas(self):
        response = await self.async_fetch("/unsafe/large-first.gif")
        assert response.code == 200
        frames = decoded_frames(response.body)
        assert [frame.size for frame in frames] == [(80, 60)] * 3
        assert frames[1].getpixel((15, 30)) == RED + (255,)
        assert frames[1].getpixel((45, 30)) == GREEN + (255,)

    @gen_test
    async def test_resize_keeps_the_proportions_of_every_frame(self):
        response = await self.async_fetch("/unsafe/0x30/opaque.gif")
        assert response.code == 200
        frames = decoded_frames(response.body)
        assert [frame.size for frame in frames] == [(40, 30)] * 3
        assert frames[1].getpixel((16, 20)) == RED + (255,)
        assert frames[1].getpixel((24, 20)) == GREEN + (255,)

    @gen_test
    async def test_filters_and_formats_get_frames_of_one_size(self):
        operations = [
            ("fill(ff0000)", "GIF"),
            ("background_color(00ff00)", "GIF"),
            ("watermark(over.png,0,0,0)", "GIF"),
            ("frame(over.png)", "GIF"),
            ("rotate(90)", "GIF"),
            ("format(webp)", "WEBP"),
            ("format(png)", "PNG"),
        ]
        if AVIF_AVAILABLE:
            operations.append(("format(avif)", "AVIF"))
        for operation, image_format in operations:
            with self.subTest(operation=operation):
                response = await self.async_fetch(
                    f"/unsafe/filters:{operation}/opaque.gif"
                )
                assert response.code == 200
                with Image.open(BytesIO(response.body)) as image:
                    assert image.format == image_format
                    assert image.n_frames == 3
                sizes = {frame.size for frame in decoded_frames(response.body)}
                assert len(sizes) == 1
                assert sorted(sizes.pop()) == sorted(SCREEN)
