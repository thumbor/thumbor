# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

from io import BytesIO
from itertools import product
from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp

from PIL import GifImagePlugin, Image, ImageSequence
from tornado.testing import gen_test

from tests.base import AVIF_AVAILABLE, HEIF_AVAILABLE, TestCase
from thumbor.config import Config

TABLE = ((0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255))


def l_shaped_gif(frames, local_tables=False):
    # Pillow's GIF writer picks the color tables and the transparent entry
    # of every frame itself, so the blocks are put together here. The shape
    # is not a rectangle because libwebp stores an opaque rectangle alone,
    # with no alpha, and Pillow reads such a WebP back as opaque
    blocks = []
    for colors, transparent, ink in frames:
        frame = Image.new("P", (32, 16), transparent)
        frame.putpalette([channel for color in colors for channel in color])
        frame.paste(ink, (8, 4, 24, 8))
        frame.paste(ink, (8, 8, 16, 12))
        if not blocks:
            header, _ = GifImagePlugin.getheader(frame, info={"duration": 100})
            blocks += header
        blocks += GifImagePlugin.getdata(
            frame,
            duration=100,
            transparency=transparent,
            disposal=2,
            include_color_table=local_tables,
        )
    return b"".join(blocks) + b";"


SOURCES = {
    "shared-table.gif": {"frames": [(TABLE, 0, ink) for ink in (1, 2, 3)]},
    "local-tables.gif": {
        "frames": [((TABLE[0], color), 0, 1) for color in TABLE[1:]],
        "local_tables": True,
    },
    "moving-entry.gif": {
        "frames": [(TABLE, 0, 1), (TABLE, 0, 2), (TABLE, 1, 3)]
    },
}


class GifFormatTransparencyTestCase(TestCase):
    def setUp(self):
        self.loader_path = Path(mkdtemp())
        self.addCleanup(rmtree, self.loader_path)
        for name, options in SOURCES.items():
            (self.loader_path / name).write_bytes(l_shaped_gif(**options))
        super().setUp()

    def get_config(self):
        return Config(
            SECURITY_KEY="ACME-SEC",
            LOADER="thumbor.loaders.file_loader",
            FILE_LOADER_ROOT_PATH=str(self.loader_path),
            STORAGE="thumbor.storages.no_storage",
            RESULT_STORAGE="thumbor.result_storages.no_storage",
        )

    @gen_test
    async def test_formats_without_a_palette_keep_the_transparency(self):
        formats = ["webp"]
        if AVIF_AVAILABLE:
            formats.append("avif")
        if HEIF_AVAILABLE:
            formats.append("heic")
        # max_bytes() reads the animation a second time
        for name, image_format, again in product(
            SOURCES, formats, ("", ":max_bytes(1)")
        ):
            filters = f"format({image_format}){again}"
            with self.subTest(source=name, filters=filters):
                response = await self.async_fetch(
                    f"/unsafe/filters:{filters}/{name}"
                )
                assert response.code == 200
                with Image.open(BytesIO(response.body)) as result:
                    frames = [
                        frame.convert("RGBA")
                        for frame in ImageSequence.Iterator(result)
                    ]
                assert len(frames) == 3
                for color, frame in zip(TABLE[1:], frames):
                    shape = frame.getpixel((12, 6))
                    assert shape.index(max(shape[:3])) == color.index(255)
                    assert shape[3] > 127
                    assert frame.getpixel((20, 10))[3] < 128
                    assert frame.getpixel((0, 0))[3] < 128
