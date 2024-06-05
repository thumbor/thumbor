#!/usr/bin/python
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
from preggy import expect
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
        expect(engine).to_be_instance_of(Engine)

    def test_load_image(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "image.jpg"), "rb") as image_file:
            buffer = image_file.read()
        image = engine.create_image(buffer)
        expect(image.format).to_equal("JPEG")
        expect(engine.subsampling).to_equal(0)

    def test_load_jp2_image(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "image.jp2"), "rb") as image_file:
            buffer = image_file.read()
        image = engine.create_image(buffer)
        expect(image.format).to_equal("JPEG2000")
        expect(engine.subsampling).to_be_null()

    def test_load_psd_image(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "1x1.psd"), "rb") as image_file:
            buffer = image_file.read()
        image = engine.create_image(buffer)
        expect(image.format).to_equal("PSD")
        expect(engine.subsampling).to_be_null()

    def test_load_tif_16bit_per_channel_lsb(self):
        engine = Engine(self.context)
        with open(
            join(STORAGE_PATH, "gradient_lsb_16bperchannel.tif"), "rb"
        ) as image_file:
            buffer = image_file.read()
        expect(buffer).not_to_equal(None)
        engine.load(buffer, None)

        final_bytes = BytesIO(engine.read())
        image_file = Image.open(final_bytes)
        expect(image_file.format).to_equal("PNG")
        expect(image_file.size).to_equal((100, 100))

    def test_load_animated_gif(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "animated.gif"), "rb") as image_file:
            buffer = image_file.read()
        expect(buffer).not_to_equal(None)
        engine.load(buffer, None)

        final_bytes = BytesIO(engine.read())
        image_file = Image.open(final_bytes)
        expect(image_file.format).to_equal("GIF")
        expect(image_file.size).to_equal((100, 100))
        expect(image_file.is_animated).to_be_true()

    def test_load_rotating_earth_gif(self):
        engine = Engine(self.context)
        with open(
            join(STORAGE_PATH, "Rotating_earth_(large).gif"), "rb"
        ) as image_file:
            buffer = image_file.read()
        expect(buffer).not_to_equal(None)
        engine.load(buffer, None)

        final_bytes = BytesIO(engine.read())
        image_file = Image.open(final_bytes)
        expect(image_file.format).to_equal("GIF")
        expect(image_file.size).to_equal((400, 400))

    def test_load_tif_16bit_per_channel_msb(self):
        engine = Engine(self.context)
        with open(
            join(STORAGE_PATH, "gradient_msb_16bperchannel.tif"), "rb"
        ) as image_file:
            buffer = image_file.read()
        expect(buffer).not_to_equal(None)
        engine.load(buffer, None)

        final_bytes = BytesIO(engine.read())
        image_file = Image.open(final_bytes)
        expect(image_file.format).to_equal("PNG")
        expect(image_file.size).to_equal((100, 100))

    def test_load_tif_8bit_per_channel(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "gradient_8bit.tif"), "rb") as image_file:
            buffer = image_file.read()
        expect(buffer).not_to_equal(None)
        engine.load(buffer, None)

        final_bytes = BytesIO(engine.read())
        image_file = Image.open(final_bytes)
        expect(image_file.format).to_equal("PNG")
        expect(image_file.size).to_equal((100, 100))

    def test_convert_png_1bit_to_png(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "1bit.png"), "rb") as image_file:
            buffer = image_file.read()
        engine.load(buffer, ".png")
        expect(engine.original_mode).to_equal(
            "P"
        )  # Note that this is not a true 1bit image, it's 8bit in black/white.

        engine.resize(10, 10)
        mode, _ = engine.image_data_as_rgb()
        expect(mode).to_equal("RGB")

        final_bytes = BytesIO(engine.read())
        mode = Image.open(final_bytes).mode
        expect(mode).to_equal("P")

    def test_convert_should_preserve_palette_mode(self):
        engine = Engine(self.context)
        with open(
            join(STORAGE_PATH, "256_color_palette.png"), "rb"
        ) as image_file:
            buffer = image_file.read()
        engine.load(buffer, ".png")
        expect(engine.original_mode).to_equal("P")

        engine.resize(10, 10)
        mode, _ = engine.image_data_as_rgb()
        expect(mode).to_equal("RGB")

        final_bytes = BytesIO(engine.read())
        mode = Image.open(final_bytes).mode
        expect(mode).to_equal("P")

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
            expect(engine.get_resize_filter()).to_equal(expected)

        cfg = Config()
        engine = Engine(Context(config=cfg))
        expect(engine.get_resize_filter()).to_equal(Image.Resampling.LANCZOS)

    def test_resize_truncated_image(self):
        engine = Engine(self.context)
        with open(
            join(STORAGE_PATH, "BlueSquare_truncated.jpg"), "rb"
        ) as image_file:
            buffer = image_file.read()
        engine.load(buffer, ".jpg")
        engine.resize(10, 10)
        mode, _ = engine.image_data_as_rgb()
        expect(mode).to_equal("RGB")

    def test_load_image_with_metadata(self):
        engine = Engine(self.context)
        with open(
            join(STORAGE_PATH, "Christophe_Henner_-_June_2016.jpg"), "rb"
        ) as image_file:
            buffer = image_file.read()

        engine.load(buffer, None)
        image = engine.image
        expect(image.format).to_equal("JPEG")
        expect(engine.metadata).Not.to_be_null()
        expect(engine.metadata.__class__.__name__).to_equal("dict")

        expect(
            engine.metadata["Exif"][piexif.ExifIFD.LensSerialNumber]
        ).to_equal("0000c139be")

        expect(engine.metadata["0th"][piexif.ImageIFD.Software]).to_equal(
            "Adobe Photoshop Lightroom 4.4 (Macintosh)"
        )

        expect(
            engine.metadata["Exif"][piexif.ExifIFD.DateTimeOriginal]
        ).to_equal("2016:06:23 13:18:05")

    def test_should_preserve_png_transparency(self):
        engine = Engine(self.context)

        with open(
            join(STORAGE_PATH, "paletted-transparent.png"), "rb"
        ) as image_file:
            buffer = image_file.read()

        engine.load(buffer, "png")
        expect(engine.original_mode).to_equal("P")
        engine.resize(200, 150)

        img = Image.open(BytesIO(engine.read(".png")))

        expect(img.mode).to_equal("P")
        expect(img.format.lower()).to_equal("png")

        transparent_pixels_count = sum(
            img.convert("RGBA")
            .split()[3]  # Get alpha channel
            .point(
                lambda x: 0 if x else 1
            )  # return 1 if pixel is transparent, 0 otherwise
            .getdata()
        )

        # Image has total of 200x150=30000 pixels. Most of them should be transparent
        expect(transparent_pixels_count).to_be_greater_than(19000)

    @skip_unless_avif
    def test_convert_jpg_to_avif(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "image.jpg"), "rb") as image_file:
            buffer = image_file.read()
        engine.load(buffer, ".jpg")
        expect(engine.image.format).to_equal("JPEG")
        avif_bytes = BytesIO(engine.read(".avif"))
        with Image.open(avif_bytes) as img:
            expect(img.format).to_equal("AVIF")

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
        expect(engine.size).to_equal((691, 212))
        avif_bytes = BytesIO(engine.read(".avif"))
        with Image.open(avif_bytes) as img:
            expect(img.format).to_equal("AVIF")
            expect(img.size).to_equal((690, 212))

    @skip_unless_heif
    def test_convert_jpg_to_heif(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "image.jpg"), "rb") as image_file:
            buffer = image_file.read()
        engine.load(buffer, ".jpg")
        expect(engine.image.format).to_equal("JPEG")
        heif_bytes = BytesIO(engine.read(".heic"))
        with Image.open(heif_bytes) as img:
            expect(img.format).to_equal("HEIF")

    @skip_unless_heif
    def test_heif_odd_dimensions(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "1bit.png"), "rb") as image_file:
            buffer = image_file.read()
        engine.load(buffer, ".png")
        expect(engine.size).to_equal((691, 212))
        heif_bytes = BytesIO(engine.read(".heic"))
        with Image.open(heif_bytes) as img:
            expect(img.format).to_equal("HEIF")
            expect(img.size).to_equal((691, 212))

    def test_should_preserve_copyright_exif_in_image(self):
        self.context.config.PRESERVE_EXIF_COPYRIGHT_INFO = True
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "thumbor-exif.png"), "rb") as image_file:
            buffer_image = image_file.read()
        engine.load(buffer_image, None)

        final_bytes = BytesIO(engine.read())
        image = Image.open(final_bytes)
        expect(image.info.get("exif")).not_to_be_null()

        exifs = piexif.load(engine.get_exif_copyright())

        expect(exifs["0th"]).not_to_be_null()
        expect(len(exifs["0th"].items())).to_equal(3)
        for k in KEEP_EXIF_COPYRIGHT_TAGS:
            expect(exifs["0th"][k]).not_to_be_null()

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

        expect(exif_original).not_to_be_null()

        exif = engine.get_exif_copyright()

        expect(exif).to_equal(exif_original)

    def test_should_read_image_without_copyright_exif(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "1bit.png"), "rb") as image_file:
            buffer = image_file.read()
        engine.load(buffer, None)

        final_bytes = BytesIO(engine.read())
        image = Image.open(final_bytes)
        expect(image.info.get("exif")).to_be_null()


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
    expect(engine.image.getpixel((0, 0))).to_equal((102, 1, 45, 0))
    avif_bytes = BytesIO(engine.read(".avif"))
    with Image.open(avif_bytes) as img:
        expect(img.format).to_equal("AVIF")
        expect(img.mode).to_equal("RGB")
        rgb_color = img.getpixel((0, 0))
        expect(rgb_color).to_equal((148, 212, 212))


@skip_unless_avif
def test_avif_convert_gray_color_profile_to_srgb():
    context = PilEngineTestCase().get_context()
    engine = Engine(context)
    with open(join(STORAGE_PATH, "grayscale-icc.jpg"), "rb") as image_file:
        buffer = image_file.read()
    engine.load(buffer, ".jpg")
    expect(engine.image.getpixel((0, 0))).to_equal(186)
    avif_bytes = BytesIO(engine.read(".avif"))
    with Image.open(avif_bytes) as img:
        expect(img.format).to_equal("AVIF")
        expect(img.mode).to_equal("RGB")
        rgb_color = img.getpixel((0, 0))
        expect(rgb_color).to_equal((200, 200, 200))
