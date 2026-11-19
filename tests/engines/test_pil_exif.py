# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

import struct
from io import BytesIO
from unittest import mock

import pytest
from PIL import ExifTags, Image, PngImagePlugin

from tests.base import AVIF_AVAILABLE, HEIF_AVAILABLE
from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines.pil import Engine

HEADER = b"Exif\x00\x00"

ASCII, SHORT, LONG, RATIONAL = 2, 3, 4, 5

ARTIST = 0x013B
COPYRIGHT = 0x8298
DATE_TIME = 0x0132
MAKE = 0x010F
X_RESOLUTION = 0x011A
EXIF_DIRECTORY = 0x8769
GPS_DIRECTORY = 0x8825
DATE_TIME_ORIGINAL = 0x9003

ARTIST_TEXT = "Maria José".encode("utf-8")
COPYRIGHT_TEXT = "© 2026 thumbor".encode("utf-8")

XMP = (
    b'<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3'
    b'.org/1999/02/22-rdf-syntax-ns#"><rdf:Description rdf:about="" xmlns:d'
    b'c="http://purl.org/dc/elements/1.1/" dc:creator="somebody"/></rdf:RDF'
    b"></x:xmpmeta>"
)

SOURCES_WITH_XMP = (
    ["JPEG", "PNG", "WEBP", "TIFF"]
    + (["AVIF"] if AVIF_AVAILABLE else [])
    + (["HEIF"] if HEIF_AVAILABLE else [])
)

OUTPUTS = (
    [".jpg", ".png", ".webp", ".gif"]
    + ([".avif"] if AVIF_AVAILABLE else [])
    + ([".heic"] if HEIF_AVAILABLE else [])
)


def tiff(*entries, data=b""):
    """A first directory at offset 8, then the data its tags name."""
    return (
        b"MM\x00*"
        + struct.pack(">LH", 8, len(entries))
        + b"".join(struct.pack(">HHL4s", *entry) for entry in entries)
        + bytes(4)
        + data
    )


def sound_exif():
    texts = {
        MAKE: b"camera",
        DATE_TIME: b"2026:11:14 10:00:00",
        ARTIST: ARTIST_TEXT,
        COPYRIGHT: COPYRIGHT_TEXT,
    }
    data_at = 8 + 2 + 12 * len(texts) + 4
    entries = []
    data = b""

    for tag, text in texts.items():
        offset = struct.pack(">L", data_at + len(data))
        entries.append((tag, ASCII, len(text) + 1, offset))
        data += text + b"\x00"

    return HEADER + tiff(*entries, data=data)


def exif_with_details():
    """A first directory, then the Exif directory it names and its text."""
    at = 8 + 2 + 12 * 2 + 4
    details = (
        struct.pack(">HHHLL", 1, DATE_TIME_ORIGINAL, ASCII, 20, at + 18)
        + bytes(4)
        + b"2016:06:23 13:18:05\x00"
    )

    return HEADER + tiff(
        (MAKE, ASCII, 3, b"me\x00\x00"),
        (EXIF_DIRECTORY, LONG, 1, struct.pack(">L", at)),
        data=details,
    )


def get_engine(**settings):
    config = Config(
        SECURITY_KEY="ACME-SEC", ENGINE="thumbor.engines.pil", **settings
    )

    return Engine(Context(config=config))


def image_with_exif(image_format, exif):
    buffer = BytesIO()
    Image.new("RGB", (64, 48), (10, 120, 200)).save(
        buffer, image_format, exif=exif
    )

    return buffer.getvalue()


def png_with_text(add, text):
    chunks = PngImagePlugin.PngInfo()
    getattr(chunks, add)("exif", text)
    buffer = BytesIO()
    Image.new("RGB", (64, 48), (10, 120, 200)).save(
        buffer, "PNG", pnginfo=chunks
    )

    return buffer.getvalue()


def jpeg_with_exif_and_xmp():
    jpeg = image_with_exif("JPEG", sound_exif())
    segment = b"http://ns.adobe.com/xap/1.0/\x00" + XMP

    return (
        jpeg[:2]
        + b"\xff\xe1"
        + struct.pack(">H", len(segment) + 2)
        + segment
        + jpeg[2:]
    )


def source_with_xmp(image_format):
    if image_format == "JPEG":
        return jpeg_with_exif_and_xmp()

    options = {"xmp": XMP}

    if image_format == "PNG":
        chunks = PngImagePlugin.PngInfo()
        chunks.add_itxt("XML:com.adobe.xmp", XMP.decode())
        options = {"pnginfo": chunks}

    if image_format == "TIFF":
        options = {"tiffinfo": {700: XMP}}

    buffer = BytesIO()
    Image.new("RGB", (64, 48), (10, 120, 200)).save(
        buffer, image_format, **options
    )

    return buffer.getvalue()


def output_exif(data):
    with Image.open(BytesIO(data)) as image:
        return dict(image.getexif())


@pytest.mark.parametrize("image_format", ["JPEG", "WEBP", "PNG"])
def test_loading_an_image_does_not_read_its_exif(image_format):
    engine = get_engine()

    with mock.patch("thumbor.engines.read_exif") as read_exif:
        engine.load(image_with_exif(image_format, sound_exif()), None)

    read_exif.assert_not_called()
    assert engine.size == (64, 48)


@pytest.mark.parametrize("image_format", ["JPEG", "WEBP", "PNG"])
def test_metadata_is_read_once_when_it_is_asked_for(image_format):
    engine = get_engine()
    engine.load(image_with_exif(image_format, sound_exif()), None)

    with mock.patch.object(
        Image.Exif, "load", autospec=True, side_effect=Image.Exif.load
    ) as pillow_load:
        metadata = engine.metadata

        assert engine.metadata is metadata

    assert pillow_load.call_count == 1
    assert isinstance(metadata, Image.Exif)
    assert metadata[MAKE] == "camera"
    assert metadata[DATE_TIME] == "2026:11:14 10:00:00"


def test_metadata_is_none_for_an_image_without_exif():
    buffer = BytesIO()
    Image.new("RGB", (64, 48)).save(buffer, "PNG")
    engine = get_engine()
    engine.load(buffer.getvalue(), None)

    assert engine.metadata is None


@pytest.mark.parametrize(
    "source, exif_type",
    [
        (image_with_exif("WEBP", b"not exif"), bytes),
        (png_with_text("add_text", "not exif"), bytes),
        (png_with_text("add_itxt", "not exif"), str),
    ],
    ids=["WebP chunk", "PNG text chunk", "PNG international text chunk"],
)
def test_metadata_is_none_for_exif_that_is_not_tiff_data(source, exif_type):
    engine = get_engine()
    engine.load(source, None)

    assert isinstance(engine.image.info["exif"], exif_type)
    assert engine.metadata is None


def test_metadata_is_of_the_image_loaded_last():
    buffer = BytesIO()
    Image.new("RGB", (64, 48)).save(buffer, "PNG")
    engine = get_engine()
    engine.load(image_with_exif("JPEG", sound_exif()), None)

    assert engine.metadata[MAKE] == "camera"

    engine.load(buffer.getvalue(), None)

    assert engine.metadata is None


def test_metadata_is_none_after_an_image_that_does_not_load():
    engine = get_engine()
    engine.load(image_with_exif("JPEG", sound_exif()), None)

    with mock.patch.object(Engine, "create_image", return_value=None):
        engine.load(b"", ".jpg")

    assert engine.metadata is None


def test_metadata_can_be_set():
    engine = get_engine()
    engine.load(image_with_exif("JPEG", sound_exif()), None)
    another = Image.Exif()
    engine.metadata = another

    assert engine.metadata is another


def test_metadata_set_while_the_image_is_created_is_kept():
    mine = Image.Exif()

    class EngineWithItsOwnMetadata(Engine):
        def create_image(self, buffer):
            image = super().create_image(buffer)
            self.metadata = mine

            return image

    engine = EngineWithItsOwnMetadata(
        Context(config=Config(SECURITY_KEY="ACME-SEC"))
    )
    engine.load(image_with_exif("JPEG", sound_exif()), None)

    assert engine.metadata is mine


def test_no_metadata_set_while_the_image_is_created_is_kept():
    class EngineWithoutMetadata(Engine):
        def create_image(self, buffer):
            image = super().create_image(buffer)
            self.metadata = None

            return image

    engine = EngineWithoutMetadata(
        Context(config=Config(SECURITY_KEY="ACME-SEC"))
    )
    engine.load(image_with_exif("JPEG", sound_exif()), None)

    assert engine.exif
    assert engine.metadata is None


def test_copyright_option_keeps_the_copyright_tags_and_no_other():
    engine = get_engine(PRESERVE_EXIF_COPYRIGHT_INFO=True)
    engine.load(image_with_exif("JPEG", sound_exif()), None)

    result = engine.read(".jpg", 80)

    assert output_exif(result) == {
        ARTIST: ARTIST_TEXT.decode("latin-1"),
        COPYRIGHT: COPYRIGHT_TEXT.decode("latin-1"),
        DATE_TIME: "2026:11:14 10:00:00",
    }
    assert ARTIST_TEXT + b"\x00" in result
    assert COPYRIGHT_TEXT + b"\x00" in result
    assert b"camera" not in result


@pytest.mark.parametrize("extension", OUTPUTS)
def test_copyright_option_keeps_the_tags_in_every_output(extension):
    engine = get_engine(PRESERVE_EXIF_COPYRIGHT_INFO=True)
    engine.load(image_with_exif("JPEG", sound_exif()), None)

    kept = [] if extension == ".gif" else [DATE_TIME, ARTIST, COPYRIGHT]

    assert sorted(output_exif(engine.read(extension, 80))) == kept


def test_copyright_option_keeps_the_whole_of_exif_that_is_not_tiff_data():
    engine = get_engine(PRESERVE_EXIF_COPYRIGHT_INFO=True)
    engine.load(png_with_text("add_text", "not exif"), None)

    assert engine.image.info["exif"] == b"not exif"

    with Image.open(BytesIO(engine.read(".png", 80))) as result:
        assert result.info["exif"] == HEADER + b"not exif"


@pytest.mark.parametrize("extension", [".png", ".jpg", ".webp"])
def test_copyright_option_keeps_nothing_of_exif_that_comes_as_text(extension):
    engine = get_engine(PRESERVE_EXIF_COPYRIGHT_INFO=True)
    engine.load(png_with_text("add_itxt", "not exif"), None)

    assert engine.image.info["exif"] == "not exif"

    with Image.open(BytesIO(engine.read(extension, 80))) as result:
        assert "exif" not in result.info


@pytest.mark.parametrize(
    "exif",
    [
        sound_exif()[: len(HEADER) + 8 + 2 + 12 * 4 + 3],
        sound_exif()[: len(HEADER) + 8 + 2 + 12 * 3],
        HEADER
        + tiff(
            (MAKE, ASCII, 7, struct.pack(">L", 8 + 2 + 12 * 3 + 4)),
            (ARTIST, ASCII, 3, b"me\x00\x00"),
            (GPS_DIRECTORY, LONG, 1, struct.pack(">L", 4096)),
            data=b"camera\x00",
        ),
        HEADER
        + tiff(
            (MAKE, ASCII, 7, struct.pack(">L", 8 + 2 + 12 * 3 + 4)),
            (ARTIST, ASCII, 3, b"me\x00\x00"),
            (X_RESOLUTION, RATIONAL, 1, struct.pack(">L", 4096)),
            data=b"camera\x00",
        ),
    ],
    ids=["no link", "entry cut", "GPS directory outside", "numbers outside"],
)
def test_copyright_option_keeps_the_whole_of_exif_that_is_broken(exif):
    engine = get_engine(PRESERVE_EXIF_COPYRIGHT_INFO=True)
    engine.load(image_with_exif("JPEG", exif), None)

    assert engine.image.info["exif"] == exif

    with Image.open(BytesIO(engine.read(".jpg", 80))) as result:
        assert result.info["exif"] == exif


def test_copyright_option_keeps_the_tags_of_exif_with_text_that_is_cut():
    exif = sound_exif()[:-30]
    engine = get_engine(PRESERVE_EXIF_COPYRIGHT_INFO=True)
    engine.load(image_with_exif("JPEG", exif), None)

    assert sorted(output_exif(engine.read(".jpg", 80))) == [DATE_TIME]


def test_copyright_option_skips_a_tag_that_is_not_text():
    exif = HEADER + tiff(
        (COPYRIGHT, SHORT, 1, b"\x00\x06\x00\x00"),
        (ARTIST, ASCII, 3, b"me\x00\x00"),
    )
    engine = get_engine(PRESERVE_EXIF_COPYRIGHT_INFO=True)
    engine.load(image_with_exif("JPEG", exif), None)

    assert output_exif(engine.read(".jpg", 80)) == {ARTIST: "me"}


@pytest.mark.parametrize(
    "extension", [extension for extension in OUTPUTS if extension != ".gif"]
)
def test_exif_is_written_when_it_is_preserved(extension):
    engine = get_engine(PRESERVE_EXIF_INFO=True)
    engine.load(image_with_exif("JPEG", sound_exif()), None)

    result = engine.read(extension, 80)

    assert output_exif(result)[MAKE] == "camera"


def test_changing_metadata_alone_does_not_change_the_exif_that_is_written():
    engine = get_engine(PRESERVE_EXIF_INFO=True)
    engine.load(image_with_exif("JPEG", exif_with_details()), None)
    engine.metadata[MAKE] = "changed"

    assert output_exif(engine.read(".jpg", 80))[MAKE] == "me"


@pytest.mark.parametrize(
    "extension", [extension for extension in OUTPUTS if extension != ".gif"]
)
def test_changed_metadata_is_written_once_the_engine_has_its_bytes(extension):
    engine = get_engine(PRESERVE_EXIF_INFO=True)
    engine.load(image_with_exif("JPEG", exif_with_details()), None)
    details = engine.metadata.get_ifd(ExifTags.IFD.Exif)

    assert details == {DATE_TIME_ORIGINAL: "2016:06:23 13:18:05"}

    engine.metadata[MAKE] = "changed"
    details[DATE_TIME_ORIGINAL] = "2001:01:01 01:01:01"
    engine.exif = engine.metadata.tobytes()

    with Image.open(BytesIO(engine.read(extension, 80))) as image:
        written = image.getexif()

        assert written[MAKE] == "changed"
        assert written.get_ifd(ExifTags.IFD.Exif) == {
            DATE_TIME_ORIGINAL: "2001:01:01 01:01:01"
        }


def test_exif_can_be_given_to_an_image_that_has_none():
    buffer = BytesIO()
    Image.new("RGB", (64, 48)).save(buffer, "JPEG")
    engine = get_engine(PRESERVE_EXIF_INFO=True)
    engine.load(buffer.getvalue(), None)
    exif = Image.Exif()
    exif[MAKE] = "thumbor"
    engine.exif = exif.tobytes()

    assert engine.metadata is None
    assert output_exif(engine.read(".jpg", 80)) == {MAKE: "thumbor"}


@pytest.mark.parametrize("image_format", SOURCES_WITH_XMP)
def test_xmp_of_the_source_is_in_the_info_of_the_image(image_format):
    engine = get_engine()
    engine.load(source_with_xmp(image_format), None)

    assert engine.image.info["xmp"] == XMP
