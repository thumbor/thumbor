# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

import struct
from os.path import abspath, dirname, join

import pytest

from thumbor.engines.extensions.jxl import (
    CONTAINER_SIGNATURE,
    MAX_PIECES,
    _exif_from_box,
    exif_to_box,
    is_jxl,
    read_header,
    split_container,
)

STORAGE_PATH = abspath(join(dirname(__file__), "../fixtures/images"))

# The first bytes of codestreams written by cjxl 0.13.0, one for each way
# of storing the size
CJXL_HEADERS = [
    ("ff0a009001001308010070006713285d", (1, 1, 0, False)),
    ("ff0a10000c0c00130801007000671328", (7, 3, 0, False)),
    ("ff0a4106001308010070006713285d92", (8, 8, 0, False)),
    ("ff0a7f060013080100e0006713285d92", (256, 256, 0, False)),
    ("ff0a6a171b0013080100108020640000", (1000, 750, 0, False)),
    ("ff0aba211d0013080100108025640000", (1920, 1080, 0, False)),
    ("ff0a024008400c0013080100108021b4", (513, 2049, 0, False)),
    ("ff0a00000f4018001308010010800cc8", (8200, 1, 0, False)),
    ("ff0a4419010818001308010010c00ccc", (3, 9001, 0, False)),
    ("ff0afcf32120282e0408020100780200", (16000, 16000, 0, False)),
    (
        "ff0a00800100080010141702080201007802000000000000",
        (262145, 1, 0, False),
    ),
    ("ff0a0fbe809f843c7ac4e10000000010", (256, 64, 0, False)),
]

# A 16x16 animation with alpha written by libjxl 0.13.0, with the optional
# fields of the header inserted bit by bit. libjxl reads the same size,
# animation flag and channel count from each of them.
ANIMATION_HEADER = (
    "ff0a43044d00604d08001000002c004b124709a5130449c20100080050000054"
)
OPTIONAL_FIELD_HEADERS = {
    "intrinsic size": (
        "ff0a4344ed0a743e340180352100400000b0002c491c25944e10240907002000"
        "40010050012c491c"
    ),
    "preview in multiples of 8": (
        "ff0a438445f8401300581302000400000bc092c45142e9044192700000020014"
        "000015c092c45142"
    ),
    "preview with an aspect ratio": (
        "ff0a43841a591300581302000400000bc092c45142e904419270000002001400"
        "0015c092c45142e9"
    ),
    "all of them at their widest": (
        "ff0a434453346f1df0d3b0863e48df7360008077f800000000d68400000100c0"
        "02b0247194503a41"
    ),
}

FIXTURES = [
    ("image.jxl", (300, 400, 0, False)),
    ("image-container.jxl", (300, 400, 0, False)),
    ("image-alpha.jxl", (100, 75, 1, False)),
    ("image-truncated.jxl", (300, 400, 0, False)),
    ("orientation-6-exif.jxl", (300, 400, 0, False)),
    ("orientation-6-jpeg.jxl", (300, 400, 0, False)),
    ("animated.jxl", (100, 100, 0, True)),
    ("extra-channels.jxl", (16, 16, 17, False)),
    ("image-jpeg-recompressed.jxl", (300, 400, 0, False)),
    ("image-linear-p3.jxl", (300, 400, 0, False)),
    ("gray-float.jxl", (32, 8, 0, False)),
    ("image-streamed.jxl", (520, 520, 0, False)),
]


def box(box_type, payload):
    return struct.pack(">I4s", 8 + len(payload), box_type) + payload


def container(*boxes):
    return (
        CONTAINER_SIGNATURE
        + box(b"ftyp", b"jxl \0\0\0\0jxl ")
        + b"".join(boxes)
    )


def piece(index, content, last=False):
    return box(
        b"jxlp",
        struct.pack(">I", index | (0x80000000 if last else 0)) + content,
    )


def read_fixture(name):
    with open(join(STORAGE_PATH, name), "rb") as fixture:
        return fixture.read()


@pytest.mark.parametrize("header, expected", CJXL_HEADERS)
def test_reads_the_size_of_a_codestream(header, expected):
    assert read_header(bytes.fromhex(header)) == expected


@pytest.mark.parametrize("name, expected", FIXTURES)
def test_reads_the_header_of_a_file(name, expected):
    assert read_header(read_fixture(name)) == expected


def test_skips_the_animation_header():
    assert read_header(bytes.fromhex(ANIMATION_HEADER)) == (16, 16, 1, True)


@pytest.mark.parametrize("field", OPTIONAL_FIELD_HEADERS)
def test_skips_the_optional_fields(field):
    header = bytes.fromhex(OPTIONAL_FIELD_HEADERS[field])

    assert read_header(header) == (16, 16, 1, True)


def test_joins_the_pieces_of_a_codestream():
    codestream = bytes.fromhex(ANIMATION_HEADER)
    chunks = [codestream[i : i + 3] for i in range(0, len(codestream), 3)]
    boxes = []

    for index, chunk in enumerate(chunks):
        boxes.append(piece(index, chunk, last=index == len(chunks) - 1))
        boxes.append(box(b"free", b"\0" * 20))

    assert split_container(container(*boxes)) == (codestream, None)
    assert read_header(container(*boxes)) == (16, 16, 1, True)


def test_joins_the_pieces_by_their_index():
    codestream = bytes.fromhex(ANIMATION_HEADER)
    buffer = container(
        piece(2, codestream[20:], last=True),
        piece(0, codestream[:5]),
        piece(1, codestream[5:20]),
    )

    assert split_container(buffer) == (codestream, None)


def test_reads_the_header_of_the_piece_the_decoder_starts_from():
    buffer = container(
        piece(1, read_fixture("image.jxl"), last=True),
        piece(0, read_fixture("animated.jxl")),
    )

    assert read_header(buffer) == (100, 100, 0, True)


def test_hands_back_the_first_exif_box():
    codestream = read_fixture("image.jxl")
    buffer = container(
        box(b"Exif", b"first"), box(b"jxlc", codestream), box(b"Exif", b"last")
    )

    assert split_container(buffer) == (codestream, b"first")


def test_takes_a_codestream_without_a_container_as_it_is():
    codestream = read_fixture("image.jxl")

    assert split_container(codestream) == (codestream, None)
    assert split_container(codestream)[0] is codestream


def test_reads_a_box_with_a_64_bit_size():
    codestream = bytes.fromhex(ANIMATION_HEADER)
    large_box = struct.pack(">I4sQ", 1, b"jxlc", 16 + len(codestream))

    assert read_header(container(large_box + codestream)) == (16, 16, 1, True)


def test_reads_a_box_that_runs_to_the_end_of_the_file():
    codestream = bytes.fromhex(ANIMATION_HEADER)
    last_box = struct.pack(">I4s", 0, b"jxlc") + codestream

    assert read_header(container(last_box)) == (16, 16, 1, True)


def test_takes_a_box_the_file_ends_before_up_to_its_end():
    codestream = read_fixture("image.jxl")
    short_box = struct.pack(">I4s", 8 + len(codestream) + 100, b"jxlc")
    huge_box = struct.pack(">I4sQ", 1, b"jxlc", 1 << 32)

    for header in (short_box, huge_box):
        buffer = container(header + codestream)

        assert split_container(buffer) == (codestream, None)


def test_ignores_what_follows_a_box_it_cannot_read():
    codestream = read_fixture("image.jxl")
    buffer = container(
        box(b"jxlc", codestream),
        b"\0\0\0\4",
        box(b"jxlc", read_fixture("animated.jxl")),
    )

    assert split_container(buffer) == (codestream, None)


@pytest.mark.parametrize(
    "buffer",
    [
        b"",
        b"\xff\x0a",
        bytes.fromhex(ANIMATION_HEADER)[:6],
        container(),
        container(box(b"Exif", b"\0" * 20)),
        container(struct.pack(">I4s", 4, b"jxlc") + b"\xff\x0a\0\0"),
        container(struct.pack(">I4s", 1, b"jxlc") + b"\0\0"),
        container(box(b"jxlp", b"\0\0")),
        container(piece(1, bytes.fromhex(ANIMATION_HEADER))),
        container(
            piece(0, bytes.fromhex(ANIMATION_HEADER)[:8]),
            piece(2, bytes.fromhex(ANIMATION_HEADER)[8:], last=True),
        ),
        container(
            piece(0, bytes.fromhex(ANIMATION_HEADER)),
            piece(0, bytes.fromhex(ANIMATION_HEADER), last=True),
        ),
        container(
            box(b"jxlc", bytes.fromhex(ANIMATION_HEADER)),
            box(b"jxlc", bytes.fromhex(ANIMATION_HEADER)),
        ),
        container(
            piece(0, bytes.fromhex(ANIMATION_HEADER), last=True),
            box(b"jxlc", bytes.fromhex(ANIMATION_HEADER)),
        ),
        container(
            piece(0, bytes.fromhex(ANIMATION_HEADER)),
            *[piece(index, b"") for index in range(1, MAX_PIECES + 1)],
        ),
        b"\x00\x00\x00\x0cjP  \r\n\x87\n",
        b"ABCDJXL \r\n\x87\n" + box(b"jxlc", bytes.fromhex(ANIMATION_HEADER)),
        box(b"JXL ", b"\r\n\x87\x0b")
        + box(b"jxlc", bytes.fromhex(ANIMATION_HEADER)),
    ],
)
def test_refuses_a_file_without_one_whole_codestream(buffer):
    with pytest.raises(ValueError):
        read_header(buffer)


def test_recognizes_both_signatures():
    assert is_jxl(read_fixture("image.jxl"))
    assert is_jxl(read_fixture("image-container.jxl"))
    assert not is_jxl(read_fixture("image.jp2"))
    assert not is_jxl(read_fixture("image.jpg"))
    assert not is_jxl(b"ABCDJXL \r\n\x87\n")


def test_finds_the_tiff_data_in_an_exif_box():
    assert _exif_from_box(b"\0\0\0\0MM\0*data") == b"MM\0*data"
    assert _exif_from_box(b"\0\0\0\2..MM\0*data") == b"MM\0*data"
    assert _exif_from_box(b"\0\0\0\x09MM\0*data") is None
    assert _exif_from_box(b"\0\0") is None
    assert _exif_from_box(None) is None


@pytest.mark.parametrize("tiff", [b"MM\0*data", b"II*\0data"])
def test_finds_the_tiff_data_in_an_exif_box_without_the_offset(tiff):
    assert _exif_from_box(tiff) == tiff


@pytest.mark.parametrize("header", [b"", b"Exif\0\0"])
def test_opens_an_exif_box_with_the_offset_of_the_tiff_data(header):
    assert exif_to_box(header + b"MM\0*data") == b"\0\0\0\0MM\0*data"
    assert _exif_from_box(exif_to_box(header + b"MM\0*data")) == b"MM\0*data"


def test_takes_as_many_pieces_as_an_encoder_writes():
    codestream = read_fixture("image.jxl")
    pieces = [piece(0, codestream)] + [
        piece(index, b"") for index in range(1, MAX_PIECES)
    ]

    assert split_container(container(*pieces)) == (codestream, None)


def test_stops_at_a_second_codestream_box():
    codestream = read_fixture("image.jxl")
    buffer = container(box(b"jxlc", codestream), box(b"jxlc", codestream))

    with pytest.raises(ValueError, match="more than one codestream"):
        split_container(buffer)
