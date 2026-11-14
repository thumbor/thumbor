# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

import logging
import struct
from io import BytesIO
from os.path import abspath, dirname, join
from types import SimpleNamespace
from unittest import mock

import pytest
from PIL import (
    ExifTags,
    Image,
    ImageChops,
    ImageCms,
    UnidentifiedImageError,
)

from tests.base import JXL_AVAILABLE, get_ssim, pillow_formats
from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines import pil
from thumbor.engines.extensions.jxl import (
    CONTAINER_SIGNATURE,
    _normalize_exif,
    engine_can_encode,
    is_jxl,
    split_container,
)
from thumbor.engines.json_engine import JSONEngine
from thumbor.engines.pil import Engine
from thumbor.utils import TRANSFORM_FLAGS

STORAGE_PATH = abspath(join(dirname(__file__), "../fixtures/images"))

requires_jxl = pytest.mark.skipif(
    not JXL_AVAILABLE, reason="JPEG XL format support not found"
)


@pytest.fixture(autouse=True)
def restore_codec_settings():
    max_pixels = Image.MAX_IMAGE_PIXELS
    yield
    Engine(get_context())
    Image.MAX_IMAGE_PIXELS = max_pixels


def get_context(**settings):
    config = Config(
        SECURITY_KEY="ACME-SEC", ENGINE="thumbor.engines.pil", **settings
    )

    return Context(config=config)


def read_fixture(name):
    with open(join(STORAGE_PATH, name), "rb") as fixture:
        return fixture.read()


def load(name, **settings):
    engine = Engine(get_context(**settings))
    engine.load(read_fixture(name), None)

    return engine


def engine_with(image, **settings):
    engine = Engine(get_context(**settings))
    engine.image = image
    engine.extension = ".png"

    return engine


def decode(buffer):
    image = Image.open(BytesIO(buffer))
    image.load()

    return image


def box(box_type, payload):
    return struct.pack(">I4s", 8 + len(payload), box_type) + payload


def piece(index, content, last=False):
    return box(
        b"jxlp",
        struct.pack(">I", index | (0x80000000 if last else 0)) + content,
    )


def container(*boxes):
    return CONTAINER_SIGNATURE + b"".join(boxes)


def noise():
    return Image.effect_noise((32, 24), 64).convert("RGB")


def jpeg_with_exif(orientation=1):
    return image_with_exif("JPEG", orientation)


def image_with_exif(image_format, orientation=1):
    exif = Image.Exif()
    exif[ExifTags.Base.Orientation] = orientation
    exif[ExifTags.Base.Make] = "thumbor"
    exif[ExifTags.Base.Copyright] = "thumbor tests"
    exif.get_ifd(ExifTags.IFD.GPSInfo)[ExifTags.GPS.GPSLatitudeRef] = "S"
    buffer = BytesIO()
    noise().save(buffer, image_format, exif=exif.tobytes())

    return buffer.getvalue()


def to_srgb(image, icc):
    return ImageCms.profileToProfile(
        image,
        ImageCms.ImageCmsProfile(BytesIO(icc)),
        ImageCms.createProfile("sRGB"),
        renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC,
        outputMode="RGB",
        flags=TRANSFORM_FLAGS,
    )


def test_refuses_an_image_over_the_pixel_limit_without_decoding_it():
    engine = Engine(get_context(MAX_PIXELS=300 * 400 - 1))

    with mock.patch.object(Image, "open") as image_open:
        assert engine.create_image(read_fixture("image.jxl")) is None

    image_open.assert_not_called()


def test_counts_the_extra_channels_against_the_pixel_limit():
    engine = Engine(get_context(MAX_PIXELS=16 * 16 * 17 - 1))

    with mock.patch.object(Image, "open") as image_open:
        assert engine.create_image(read_fixture("extra-channels.jxl")) is None

    image_open.assert_not_called()


def test_refuses_a_header_it_cannot_read():
    engine = Engine(get_context())

    with mock.patch.object(Image, "open") as image_open:
        with pytest.raises(UnidentifiedImageError):
            engine.create_image(b"\xff\x0a")

    image_open.assert_not_called()


@requires_jxl
@pytest.mark.parametrize("name", ["image.jxl", "image-container.jxl"])
def test_loads_an_image_at_the_pixel_limit(name):
    engine = load(name, MAX_PIXELS=300 * 400)

    assert engine.extension == ".jxl"
    assert engine.size == (300, 400)
    assert engine.image.mode == "RGB"


@requires_jxl
def test_loads_extra_channels_within_the_pixel_limit():
    engine = load("extra-channels.jxl", MAX_PIXELS=16 * 16 * 17)

    assert engine.size == (16, 16)


@requires_jxl
def test_does_not_count_the_alpha_channel_against_the_pixel_limit():
    engine = load("image-alpha.jxl", MAX_PIXELS=100 * 75)

    assert engine.image.mode == "RGBA"


@requires_jxl
def test_loads_any_size_without_a_pixel_limit():
    engine = load("image.jxl", MAX_PIXELS=None)

    assert engine.size == (300, 400)


@requires_jxl
def test_refuses_a_truncated_image():
    engine = Engine(get_context())
    buffer = read_fixture("image-truncated.jxl")

    with pytest.raises(UnidentifiedImageError):
        engine.create_image(buffer)


@requires_jxl
def test_refuses_a_codestream_the_file_ends_before():
    engine = Engine(get_context())
    codestream = read_fixture("image.jxl")
    buffer = container(box(b"jxlc", codestream)[: 8 + len(codestream) // 2])

    with pytest.raises(UnidentifiedImageError):
        engine.create_image(buffer)


def test_refuses_an_animation_without_decoding_it():
    engine = Engine(get_context())
    buffer = read_fixture("animated.jxl")

    with mock.patch.object(Image, "open") as image_open:
        with pytest.raises(UnidentifiedImageError):
            engine.create_image(buffer)

    image_open.assert_not_called()


def test_refuses_what_only_the_plugin_would_take_for_jxl():
    engine = Engine(get_context())
    buffer = b"ABCD" + read_fixture("image-container.jxl")[4:]

    with pytest.raises(UnidentifiedImageError):
        engine.create_image(buffer)


def test_loads_another_format_the_plugin_would_take_for_jxl():
    engine = Engine(get_context())
    engine.load(b"P6\n#JXL\n4 4\n255\n" + bytes(48), None)

    assert engine.size == (4, 4)


def test_checks_the_header_the_decoder_starts_from():
    engine = Engine(get_context())
    buffer = container(
        piece(1, read_fixture("image.jxl"), last=True),
        piece(0, read_fixture("animated.jxl")),
    )

    with mock.patch.object(Image, "open") as image_open:
        with pytest.raises(UnidentifiedImageError):
            engine.create_image(buffer)

    image_open.assert_not_called()


@requires_jxl
@pytest.mark.parametrize(
    "name",
    [
        "image-container.jxl",
        "image-jpeg-recompressed.jxl",
        "image-streamed.jxl",
    ],
)
def test_hands_the_decoder_the_codestream_alone(name):
    engine = Engine(get_context())
    buffer = read_fixture(name)

    with mock.patch.object(Image, "open", wraps=Image.open) as image_open:
        engine.create_image(buffer)

    (stream,), _ = image_open.call_args

    assert stream.getvalue() == split_container(buffer)[0]
    assert stream.getvalue().startswith(b"\xff\x0a")


@requires_jxl
def test_loads_a_streamed_file_as_the_plugin_reads_it():
    engine = load("image-streamed.jxl")

    assert engine.size == (520, 520)
    assert (
        engine.image.tobytes()
        == decode(read_fixture("image-streamed.jxl")).tobytes()
    )


@requires_jxl
def test_loads_a_recompressed_jpeg_from_its_codestream():
    engine = load("image-jpeg-recompressed.jxl")
    jpeg = Image.open(join(STORAGE_PATH, "image.jpg"))

    assert engine.image.mode == "RGB"
    assert get_ssim(engine.image, jpeg) > 0.99


@requires_jxl
def test_scales_float_samples():
    engine = load("gray-float.jxl")

    assert engine.image.mode == "L"
    assert engine.image.getextrema() == (0, 255)


@requires_jxl
def test_drops_the_profile_the_decoder_makes_up_for_srgb():
    assert load("image.jxl").icc_profile is None
    assert load("image-linear-p3.jxl").icc_profile is not None


@requires_jxl
def test_resets_the_orientation_the_decoder_already_applied():
    engine = load("orientation-6-exif.jxl")

    assert engine.size == (400, 300)
    assert engine.get_orientation() == 1

    exif = Image.Exif()
    exif.load(engine.exif)

    assert exif[ExifTags.Base.Copyright] == "thumbor tests"


@requires_jxl
def test_loads_a_recompressed_jpeg_as_the_decoder_orients_it():
    engine = load("orientation-6-jpeg.jxl")

    assert engine.size == (400, 300)
    assert engine.get_orientation() is None


def test_drops_exif_it_cannot_read():
    image = Image.new("RGB", (1, 1))
    image.info["exif"] = b"II*\x00garbage"

    _normalize_exif(image)

    assert "exif" not in image.info


@requires_jxl
def test_writes_no_exif_by_default():
    engine = Engine(get_context())
    engine.load(jpeg_with_exif(), None)

    assert "exif" not in decode(engine.read(".jxl", 80)).info


@requires_jxl
def test_writes_the_exif_it_is_asked_to_preserve():
    engine = Engine(get_context(PRESERVE_EXIF_INFO=True))
    engine.load(jpeg_with_exif(), None)

    exif = decode(engine.read(".jxl", 80)).getexif()

    assert exif[ExifTags.Base.Make] == "thumbor"
    assert exif[ExifTags.Base.Copyright] == "thumbor tests"


@requires_jxl
@pytest.mark.parametrize(
    "settings",
    [{"PRESERVE_EXIF_INFO": True}, {"PRESERVE_EXIF_COPYRIGHT_INFO": True}],
)
def test_writes_the_exif_box_with_the_offset_of_the_tiff_data(settings):
    engine = Engine(get_context(**settings))
    engine.load(jpeg_with_exif(), None)

    _, exif_box = split_container(engine.read(".jxl", 80))

    assert exif_box[:4] == b"\0\0\0\0"
    assert exif_box[4:8] in (b"II*\0", b"MM\0*")


@requires_jxl
@pytest.mark.parametrize(
    "settings",
    [{"PRESERVE_EXIF_INFO": True}, {"PRESERVE_EXIF_COPYRIGHT_INFO": True}],
)
def test_reads_back_the_exif_it_wrote(settings):
    engine = Engine(get_context(**settings))
    engine.load(jpeg_with_exif(), None)
    written = Engine(get_context())
    written.load(engine.read(".jxl", 80), None)

    exif = Image.Exif()
    exif.load(written.exif)

    assert exif[ExifTags.Base.Copyright] == "thumbor tests"


@requires_jxl
def test_reads_the_exif_of_a_file_the_plugin_wrote():
    engine = Engine(get_context())
    engine.load(image_with_exif("JXL"), None)

    exif = Image.Exif()
    exif.load(engine.exif)

    assert exif[ExifTags.Base.Copyright] == "thumbor tests"


@requires_jxl
@pytest.mark.parametrize("image_format", ["JPEG", "WEBP", "PNG"])
@pytest.mark.parametrize(
    "settings, size, orientation",
    [
        ({"PRESERVE_EXIF_INFO": True}, (24, 32), 1),
        ({}, (32, 24), None),
    ],
)
def test_rotates_the_pixels_when_it_writes_the_orientation(
    settings, size, orientation, image_format
):
    engine = Engine(get_context(**settings))
    engine.load(image_with_exif(image_format, orientation=6), None)

    result = decode(engine.read(".jxl", 80))

    assert result.size == size
    assert result.getexif().get(ExifTags.Base.Orientation) == orientation


@requires_jxl
def test_writes_only_the_copyright_it_is_asked_to_preserve():
    engine = Engine(get_context(PRESERVE_EXIF_COPYRIGHT_INFO=True))
    engine.load(jpeg_with_exif(), None)

    exif = decode(engine.read(".jxl", 80)).getexif()

    assert ExifTags.Base.Make not in exif
    assert exif[ExifTags.Base.Copyright] == "thumbor tests"


@requires_jxl
@pytest.mark.parametrize(
    "mode, expected",
    [
        ("RGB", "RGB"),
        ("RGBA", "RGBA"),
        ("L", "L"),
        ("LA", "LA"),
        ("I;16", "L"),
        ("P", "RGB"),
        ("PA", "RGBA"),
        ("1", "RGB"),
        ("CMYK", "RGB"),
        ("I", "RGB"),
        ("F", "L"),
        ("YCbCr", "RGB"),
        ("LAB", "RGB"),
        ("HSV", "RGB"),
        ("RGBX", "RGB"),
    ],
)
def test_writes_every_mode(mode, expected):
    engine = engine_with(Image.new(mode, (8, 8)))

    assert decode(engine.read(".jxl", 80)).mode == expected


@requires_jxl
def test_scales_16_bit_samples_down_to_8():
    samples = struct.pack("<3H", 0x2000, 0x8000, 0xE000)
    engine = engine_with(Image.frombytes("I;16", (3, 1), samples))

    result = decode(engine.read(".jxl", 100))

    assert list(result.tobytes()) == [0x1F, 0x7F, 0xDF]


@requires_jxl
def test_writes_a_transparent_palette_with_alpha():
    image = Image.new("P", (8, 8))
    image.info["transparency"] = 0
    engine = engine_with(image)

    assert decode(engine.read(".jxl", 80)).mode == "RGBA"


@requires_jxl
@pytest.mark.parametrize("quality", [100, 101])
def test_encodes_without_loss_from_quality_100(quality):
    source = noise()
    engine = engine_with(source.copy())

    assert decode(engine.read(".jxl", quality)).tobytes() == source.tobytes()


@requires_jxl
@pytest.mark.parametrize("quality", [0, 80, 99, "keep"])
def test_encodes_with_loss_below_quality_100(quality):
    source = noise()
    engine = engine_with(source.copy())
    result = decode(engine.read(".jxl", quality))

    assert result.size == source.size
    assert result.tobytes() != source.tobytes()


@requires_jxl
def test_converts_a_wide_gamut_source_to_srgb():
    engine = load("image-linear-p3.jpg")
    source = engine.image.copy()
    expected = to_srgb(source, engine.icc_profile)

    result = decode(engine.read(".jxl", 100))

    assert result.tobytes() == expected.tobytes()
    assert ImageChops.difference(result, source).getbbox() is not None
    assert engine.icc_profile is None


@requires_jxl
def test_leaves_an_srgb_source_as_it_is():
    source = noise()
    profile = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB"))
    buffer = BytesIO()
    source.save(buffer, "PNG", icc_profile=profile.tobytes())
    engine = Engine(get_context())
    engine.load(buffer.getvalue(), None)

    assert decode(engine.read(".jxl", 100)).tobytes() == source.tobytes()


@requires_jxl
def test_does_not_convert_a_source_whose_profile_was_stripped():
    engine = load("image-linear-p3.jpg")
    source = engine.image.copy()
    engine.strip_icc()

    assert decode(engine.read(".jxl", 100)).tobytes() == source.tobytes()


@requires_jxl
def test_converts_a_source_a_filter_turned_gray():
    engine = load("image-linear-p3.jpg")
    icc = engine.icc_profile
    engine.convert_to_grayscale()
    source = engine.image.copy()
    expected = to_srgb(source.convert("RGB"), icc).convert("L")

    result = decode(engine.read(".jxl", 100))

    assert result.mode == "L"
    assert result.tobytes() == expected.tobytes()
    assert result.tobytes() != source.tobytes()


@requires_jxl
def test_converts_a_gray_source_a_filter_turned_rgb():
    expected = decode(load("grayscale-icc.jpg").read(".jxl", 100))
    engine = load("grayscale-icc.jpg")
    engine.image_data_as_rgb()

    result = decode(engine.read(".jxl", 100))

    assert result.mode == "RGB"
    assert result.convert("L").tobytes() == expected.tobytes()


@requires_jxl
def test_writes_an_image_whose_profile_cannot_be_used():
    source = noise()
    profile = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB"))
    engine = engine_with(source.copy())
    engine.icc_profile = profile.tobytes().replace(b"rXYZ", b"qXYZ", 1)

    assert decode(engine.read(".jxl", 100)).tobytes() == source.tobytes()


@requires_jxl
def test_converts_a_gray_source_and_keeps_it_gray():
    engine = load("grayscale-icc.jpg")
    source = engine.image.copy()
    expected = to_srgb(source, engine.icc_profile).convert("L")

    result = decode(engine.read(".jxl", 100))

    assert result.mode == "L"
    assert result.tobytes() == expected.tobytes()
    assert result.tobytes() != source.tobytes()


@requires_jxl
def test_converts_a_cmyk_source_through_its_profile():
    engine = load("cmyk-icc.jpg")
    source = engine.image.copy()
    expected = to_srgb(source, engine.icc_profile)

    result = decode(engine.read(".jxl", 100))

    assert result.tobytes() == expected.tobytes()
    assert result.tobytes() != source.convert("RGB").tobytes()


def test_falls_back_to_the_source_format_without_an_encoder(caplog):
    engine = load("image.jpg")

    with pillow_formats(), caplog.at_level(logging.WARNING):
        result = decode(engine.read(".jxl", 80))

    assert result.format == "JPEG"
    assert caplog.record_tuples == [
        (
            "thumbor",
            logging.WARNING,
            "[PILEngine] JPEG XL encoding unavailable, defaulting to .jpg",
        )
    ]


@requires_jxl
@pytest.mark.parametrize(
    "name, expected", [("image.jxl", "JPEG"), ("image-alpha.jxl", "PNG")]
)
def test_falls_back_to_a_default_format_for_a_jxl_source(name, expected):
    engine = load(name)

    with pillow_formats(opener=Image.OPEN["JXL"]):
        result = decode(engine.read(".jxl", 80))

    assert result.format == expected


@pytest.mark.parametrize(
    "settings, threads, effort",
    [
        ({}, 1, 3),
        ({"JXL_THREADS": 4, "JXL_EFFORT": 5}, 4, 5),
        ({"JXL_THREADS": None, "JXL_EFFORT": None}, -1, None),
    ],
)
def test_passes_the_settings_to_the_encoder(settings, threads, effort):
    engine = engine_with(Image.new("RGB", (8, 8)), **settings)

    with (
        pillow_formats(saver=mock.sentinel.saver),
        mock.patch.object(Image.Image, "save") as save,
    ):
        engine.read(".jxl", 80)

    options = save.call_args.kwargs

    assert options["num_threads"] == threads
    assert options.get("effort") == effort
    assert options["quality"] == 80
    assert options["exif"] == b""


@requires_jxl
@pytest.mark.parametrize(
    "settings, threads",
    [({}, 1), ({"JXL_THREADS": 4}, 4), ({"JXL_THREADS": None}, -1)],
)
def test_passes_the_threads_to_the_decoder(settings, threads):
    Engine(get_context(**settings))

    assert pil.pillow_jxl.JpegXLImagePlugin.DECODE_THREADS == threads


def test_json_engine_asks_the_engine_it_wraps():
    engine = engine_with(Image.new("RGB", (8, 8)))
    json_engine = JSONEngine(engine, "image.jxl")

    for enabled in (True, False):
        with mock.patch.object(engine, "jxl_enabled", return_value=enabled):
            assert json_engine.jxl_enabled() is enabled


def test_an_engine_older_than_jxl_cannot_write_it():
    assert not engine_can_encode(SimpleNamespace())
    assert not engine_can_encode(SimpleNamespace(jxl_enabled=lambda: False))
    assert engine_can_encode(SimpleNamespace(jxl_enabled=lambda: True))


def test_keeps_the_plugin_from_claiming_other_formats():
    with pillow_formats(opener=(mock.sentinel.factory, None)):
        Engine(get_context())

        assert Image.OPEN["JXL"] == (mock.sentinel.factory, is_jxl)
        assert Image.ID.count("JXL") == 1


def test_tells_whether_it_can_write_jxl():
    engine = Engine(get_context())

    with pillow_formats(saver=mock.sentinel.saver):
        assert engine.jxl_enabled()

    with pillow_formats():
        assert not engine.jxl_enabled()
