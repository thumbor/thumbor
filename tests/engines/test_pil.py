# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

# pylint: disable=unsupported-membership-test

from io import BytesIO
from os.path import abspath, dirname, join
from unittest import TestCase, mock

import piexif
from PIL import Image
import pytest

from tests.base import (
    skip_unless_avif,
    skip_unless_avif_encoder,
    skip_unless_heif,
)
from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines.pil import Engine, KEEP_EXIF_COPYRIGHT_TAGS

FIXTURES_PATH = abspath(join(dirname(__file__), "../fixtures/"))
STORAGE_PATH = join(FIXTURES_PATH, "images")


class PilEngineTestCase(TestCase):
    def get_context(self):
        cfg = Config(
            SECURITY_KEY="ACME-SEC",
            ENGINE="thumbor.engines.pil",
            IMAGE_METADATA_READ_FORMATS="exif,xmp",
        )
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = STORAGE_PATH
        cfg.STORAGE = "thumbor.storages.no_storage"

        return Context(config=cfg)

    def setUp(self):
        self.context = self.get_context()

    def test_create_engine(self):
        engine = Engine(self.context)
        assert isinstance(engine, Engine)

    def test_load_image(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "image.jpg"), "rb") as image_file:
            buffer = image_file.read()
        image = engine.create_image(buffer)
        assert image.format == "JPEG"
        assert engine.subsampling == 0

    def test_load_jp2_image(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "image.jp2"), "rb") as image_file:
            buffer = image_file.read()
        image = engine.create_image(buffer)
        assert image.format == "JPEG2000"
        assert engine.subsampling is None

    def test_load_psd_image(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "1x1.psd"), "rb") as image_file:
            buffer = image_file.read()
        image = engine.create_image(buffer)
        assert image.format == "PSD"
        assert engine.subsampling is None

    def test_load_tif_16bit_per_channel_lsb(self):
        engine = Engine(self.context)
        with open(
            join(STORAGE_PATH, "gradient_lsb_16bperchannel.tif"), "rb"
        ) as image_file:
            buffer = image_file.read()
        assert buffer is not None
        engine.load(buffer, None)

        final_bytes = BytesIO(engine.read())
        image_file = Image.open(final_bytes)
        assert image_file.format == "PNG"
        assert image_file.size == (100, 100)

    def test_load_animated_gif(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "animated.gif"), "rb") as image_file:
            buffer = image_file.read()
        assert buffer is not None
        engine.load(buffer, None)

        final_bytes = BytesIO(engine.read())
        image_file = Image.open(final_bytes)
        assert image_file.format == "GIF"
        assert image_file.size == (100, 100)
        assert image_file.is_animated

    def test_load_rotating_earth_gif(self):
        engine = Engine(self.context)
        with open(
            join(STORAGE_PATH, "Rotating_earth_(large).gif"), "rb"
        ) as image_file:
            buffer = image_file.read()
        assert buffer is not None
        engine.load(buffer, None)

        final_bytes = BytesIO(engine.read())
        image_file = Image.open(final_bytes)
        assert image_file.format == "GIF"
        assert image_file.size == (400, 400)

    def test_load_tif_16bit_per_channel_msb(self):
        engine = Engine(self.context)
        with open(
            join(STORAGE_PATH, "gradient_msb_16bperchannel.tif"), "rb"
        ) as image_file:
            buffer = image_file.read()
        assert buffer is not None
        engine.load(buffer, None)

        final_bytes = BytesIO(engine.read())
        image_file = Image.open(final_bytes)
        assert image_file.format == "PNG"
        assert image_file.size == (100, 100)

    def test_load_tif_8bit_per_channel(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "gradient_8bit.tif"), "rb") as image_file:
            buffer = image_file.read()
        assert buffer is not None
        engine.load(buffer, None)

        final_bytes = BytesIO(engine.read())
        image_file = Image.open(final_bytes)
        assert image_file.format == "PNG"
        assert image_file.size == (100, 100)

    def test_convert_png_1bit_to_png(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "1bit.png"), "rb") as image_file:
            buffer = image_file.read()
        engine.load(buffer, ".png")
        assert engine.original_mode == "P"

        engine.resize(10, 10)
        mode, _ = engine.image_data_as_rgb()
        assert mode == "RGB"

        final_bytes = BytesIO(engine.read())
        mode = Image.open(final_bytes).mode
        assert mode == "P"

    def test_convert_should_preserve_palette_mode(self):
        engine = Engine(self.context)
        with open(
            join(STORAGE_PATH, "256_color_palette.png"), "rb"
        ) as image_file:
            buffer = image_file.read()
        engine.load(buffer, ".png")
        assert engine.original_mode == "P"

        engine.resize(10, 10)
        mode, _ = engine.image_data_as_rgb()
        assert mode == "RGB"

        final_bytes = BytesIO(engine.read())
        mode = Image.open(final_bytes).mode
        assert mode == "P"

    def test_can_set_resampling_filter(self):
        to_test = {
            "LANCZOS": Image.Resampling.LANCZOS,
            "NEAREST": Image.Resampling.NEAREST,
            "BiLinear": Image.Resampling.BILINEAR,
            "bicubic": Image.Resampling.BICUBIC,
            "garbage": Image.Resampling.LANCZOS,
        }

        if hasattr(Image, "HAMMING"):
            to_test["HAMMING"] = Image.Resampling.HAMMING

        for setting, expected in to_test.items():
            cfg = Config(PILLOW_RESAMPLING_FILTER=setting)
            engine = Engine(Context(config=cfg))
            assert engine.get_resize_filter() == expected

        cfg = Config()
        engine = Engine(Context(config=cfg))
        assert engine.get_resize_filter() == Image.Resampling.LANCZOS

    def test_resize_truncated_image(self):
        engine = Engine(self.context)
        with open(
            join(STORAGE_PATH, "BlueSquare_truncated.jpg"), "rb"
        ) as image_file:
            buffer = image_file.read()
        engine.load(buffer, ".jpg")
        engine.resize(10, 10)
        mode, _ = engine.image_data_as_rgb()
        assert mode == "RGB"

    def test_load_image_with_metadata(self):
        engine = Engine(self.context)
        with open(
            join(STORAGE_PATH, "Christophe_Henner_-_June_2016.jpg"), "rb"
        ) as image_file:
            buffer = image_file.read()

        engine.load(buffer, None)
        image = engine.image
        assert image.format == "JPEG"
        assert engine.metadata is not None
        assert engine.metadata.__class__.__name__ == "dict"

        assert (
            engine.metadata["Exif"][piexif.ExifIFD.LensSerialNumber]
            == b"0000c139be"
        )
        assert (
            engine.metadata["0th"][piexif.ImageIFD.Software]
            == b"Adobe Photoshop Lightroom 4.4 (Macintosh)"
        )
        assert (
            engine.metadata["Exif"][piexif.ExifIFD.DateTimeOriginal]
            == b"2016:06:23 13:18:05"
        )

    def test_should_preserve_png_transparency(self):
        engine = Engine(self.context)

        with open(
            join(STORAGE_PATH, "paletted-transparent.png"), "rb"
        ) as image_file:
            buffer = image_file.read()

        engine.load(buffer, "png")
        assert engine.original_mode == "P"
        engine.resize(200, 150)

        img = Image.open(BytesIO(engine.read(".png")))

        assert img.mode == "P"
        assert img.format.lower() == "png"

        transparent_pixels_count = sum(
            img.convert("RGBA")
            .split()[3]
            .point(lambda x: 0 if x else 1)
            .getdata()
        )
        assert transparent_pixels_count > 19000

    @skip_unless_avif
    def test_convert_jpg_to_avif(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "image.jpg"), "rb") as image_file:
            buffer = image_file.read()
        engine.load(buffer, ".jpg")
        assert engine.image.format == "JPEG"
        avif_bytes = BytesIO(engine.read(".avif"))
        with Image.open(avif_bytes) as img:
            assert img.format == "AVIF"

    @skip_unless_avif_encoder("aom")
    def test_avif_codec_setting(self):
        self.context.config.AVIF_CODEC = "aom"
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "image.jpg"), "rb") as image_file:
            buffer = image_file.read()
        engine.load(buffer, ".jpg")

        with mock.patch("PIL.ImageFile.ImageFile.save") as mock_save:
            engine.read(".avif")
            mock_save.assert_called_once()
            assert mock_save.call_args[1].get("codec") == "aom"

    @skip_unless_avif
    def test_avif_speed_setting(self):
        self.context.config.AVIF_SPEED = 5
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "image.jpg"), "rb") as image_file:
            buffer = image_file.read()
        engine.load(buffer, ".jpg")

        with mock.patch("PIL.ImageFile.ImageFile.save") as mock_save:
            engine.read(".avif")
            mock_save.assert_called_once()
            assert mock_save.call_args[1].get("speed") == 5

    @skip_unless_avif_encoder("svt")
    def test_avif_svt_odd_dimensions(self):
        self.context.config.AVIF_CODEC = "svt"
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "1bit.png"), "rb") as image_file:
            buffer = image_file.read()
        engine.load(buffer, ".png")
        assert engine.size == (691, 212)
        avif_bytes = BytesIO(engine.read(".avif"))
        with Image.open(avif_bytes) as img:
            assert img.format == "AVIF"
            assert img.size == (690, 212)

    @skip_unless_heif
    def test_convert_jpg_to_heif(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "image.jpg"), "rb") as image_file:
            buffer = image_file.read()
        engine.load(buffer, ".jpg")
        assert engine.image.format == "JPEG"
        heif_bytes = BytesIO(engine.read(".heic"))
        with Image.open(heif_bytes) as img:
            assert img.format == "HEIF"

    @skip_unless_heif
    def test_heif_odd_dimensions(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "1bit.png"), "rb") as image_file:
            buffer = image_file.read()
        engine.load(buffer, ".png")
        assert engine.size == (691, 212)
        heif_bytes = BytesIO(engine.read(".heic"))
        with Image.open(heif_bytes) as img:
            assert img.format == "HEIF"
            assert img.size == (691, 212)

    def test_should_preserve_copyright_exif_in_image(self):
        self.context.config.PRESERVE_EXIF_COPYRIGHT_INFO = True
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "thumbor-exif.png"), "rb") as image_file:
            buffer_image = image_file.read()
        engine.load(buffer_image, None)

        final_bytes = BytesIO(engine.read())
        image = Image.open(final_bytes)
        assert image.info.get("exif") is not None

        exifs = piexif.load(engine.get_exif_copyright())

        assert exifs["0th"] is not None
        assert len(exifs["0th"].items()) == 3
        for k in KEEP_EXIF_COPYRIGHT_TAGS:
            assert exifs["0th"][k] is not None

    def test_should_preserve_copyright_exif_in_image_with_broken_exif_tag(
        self,
    ):
        self.context.config.PRESERVE_EXIF_COPYRIGHT_INFO = True
        engine = Engine(self.context)
        with open(
            join(STORAGE_PATH, "broken-exif-tag.jpg"), "rb"
        ) as image_file:
            buffer_image = image_file.read()
        engine.load(buffer_image, None)

        final_bytes = BytesIO(engine.read())
        image = Image.open(final_bytes)
        exif_original = image.info.get("exif")

        assert exif_original is not None

        exif = engine.get_exif_copyright()

        assert exif == exif_original

    def test_should_read_image_without_copyright_exif(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "1bit.png"), "rb") as image_file:
            buffer = image_file.read()
        engine.load(buffer, None)

        final_bytes = BytesIO(engine.read())
        image = Image.open(final_bytes)
        assert image.info.get("exif") is None


@skip_unless_avif_encoder("svt")
@pytest.mark.parametrize(
    "image_basename", ("20x20.jpg", "Christophe_Henner_-_June_2016.jpg")
)
def test_avif_svt_codec_fallback(image_basename):
    context = PilEngineTestCase().get_context()
    context.config.AVIF_CODEC = "svt"
    engine = Engine(context)
    with open(join(STORAGE_PATH, image_basename), "rb") as image_file:
        buffer = image_file.read()
    engine.load(buffer, ".jpg")

    with mock.patch("PIL.ImageFile.ImageFile.save") as mock_save:
        engine.read(".avif")
        mock_save.assert_called_once()
        assert mock_save.call_args[1].get("codec") == "auto"


@pytest.mark.xfail(reason="flaky test depending on the state of a dependency")
@skip_unless_avif
@pytest.mark.parametrize("srgb_profile", [None, "srgb.icc"])
def test_avif_convert_cmyk_color_profile_to_srgb(srgb_profile):
    context = PilEngineTestCase().get_context()
    if srgb_profile:
        context.config.SRGB_PROFILE = join(FIXTURES_PATH, srgb_profile)
    engine = Engine(context)
    with open(join(STORAGE_PATH, "cmyk-icc.jpg"), "rb") as image_file:
        buffer = image_file.read()
    engine.load(buffer, ".jpg")
    assert engine.image.getpixel((0, 0)) == (102, 1, 45, 0)
    avif_bytes = BytesIO(engine.read(".avif"))
    with Image.open(avif_bytes) as img:
        assert img.format == "AVIF"
        assert img.mode == "RGB"
        rgb_color = img.getpixel((0, 0))
        assert rgb_color == (148, 212, 212)


@skip_unless_avif
def test_avif_convert_gray_color_profile_to_srgb():
    context = PilEngineTestCase().get_context()
    engine = Engine(context)
    with open(join(STORAGE_PATH, "grayscale-icc.jpg"), "rb") as image_file:
        buffer = image_file.read()
    engine.load(buffer, ".jpg")
    assert engine.image.getpixel((0, 0)) == 186
    avif_bytes = BytesIO(engine.read(".avif"))
    with Image.open(avif_bytes) as img:
        assert img.format == "AVIF"
        assert img.mode == "RGB"
        rgb_color = img.getpixel((0, 0))
        assert rgb_color == (200, 200, 200)
