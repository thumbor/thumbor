# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

import struct
from os.path import abspath, dirname, join
from unittest import mock

import pytest
from PIL import ExifTags, Image, PngImagePlugin

from thumbor.engines.extensions.exif import keep_tags, read_exif

STORAGE_PATH = abspath(join(dirname(__file__), "../fixtures/images"))

HEADER = b"Exif\x00\x00"

ASCII, SHORT, LONG, UNDEFINED, UTF8 = 2, 3, 4, 7, 129

ARTIST = 0x013B
COPYRIGHT = 0x8298
DATE_TIME = 0x0132
MAKE = 0x010F
ORIENTATION = 0x0112
X_RESOLUTION = 0x011A
EXIF_VERSION = 0x9000
EXIF_DIRECTORY = 0x8769
GPS_DIRECTORY = 0x8825
INTEROPERABILITY_DIRECTORY = 0xA005

DIRECTORIES = [
    ExifTags.IFD.Exif,
    ExifTags.IFD.GPSInfo,
    ExifTags.IFD.Interop,
    ExifTags.IFD.IFD1,
]

EXIF_FIXTURES = [
    "10_years_of_Wikipedia_by_Guillaume_Paumier.jpg",
    "BlueSquare_truncated.jpg",
    "Christophe_Henner_-_June_2016.jpg",
    "Giunchedi%2C_Filippo_January_2015_01-cmyk-orientation-exif.jpg",
    "broken-exif-tag.jpg",
    "thumbor-exif.png",
]

SOUND = (ORIENTATION, SHORT, 1, b"\x00\x06\x00\x00")


def directory(*entries, following=0, declared=None):
    return (
        struct.pack(">H", len(entries) if declared is None else declared)
        + b"".join(
            struct.pack(">HHL4s", tag, value_type, values, value)
            for tag, value_type, values, value in entries
        )
        + struct.pack(">L", following)
    )


def tiff(*directories):
    """Lays directories out one after the other, the first at offset 8."""
    return b"MM\x00*" + struct.pack(">L", 8) + b"".join(directories)


def pointer(tag, offset):
    return (tag, LONG, 1, struct.pack(">L", offset))


def directory_of(exif, tag):
    try:
        return exif.get_ifd(tag)
    except KeyError:
        # Before Pillow 13, get_ifd raises for EXIF that has no
        # Interoperability directory
        return {}


def view(exif):
    return repr(
        (
            sorted(dict(exif).items()),
            [sorted(directory_of(exif, tag).items()) for tag in DIRECTORIES],
        )
    )


def read_with_pillow_alone(data):
    exif = Image.Exif()
    exif.load(data)

    return exif


def assert_refused(data):
    with mock.patch.object(Image.Exif, "load") as pillow_load:
        with pytest.raises(ValueError):
            read_exif(data)

    pillow_load.assert_not_called()


def fixture_exif(name):
    with Image.open(join(STORAGE_PATH, name)) as image:
        return image.info["exif"]


def little_endian(header):
    """Little-endian EXIF whose only directory comes after its text."""
    text = b"Maria\x00"

    return (
        header
        + struct.pack("<L", 8 + len(text))
        + text
        + struct.pack("<HHHLL", 1, ARTIST, ASCII, len(text), 8)
        + bytes(4)
    )


@pytest.mark.parametrize("name", EXIF_FIXTURES)
def test_reads_what_pillow_reads(name):
    exif = fixture_exif(name)
    expected = view(read_with_pillow_alone(exif))

    assert exif.startswith(HEADER)
    assert view(read_exif(exif)) == expected
    assert view(read_exif(exif[len(HEADER) :])) == expected


def test_reads_every_directory():
    first = directory(
        pointer(EXIF_DIRECTORY, 8 + 30),
        pointer(GPS_DIRECTORY, 8 + 30 + 18),
        following=8 + 30 + 18 + 18 + 18,
    )
    exif = directory(pointer(INTEROPERABILITY_DIRECTORY, 8 + 30 + 18 + 18))
    gps = directory((0x0001, ASCII, 2, b"N\x00\x00\x00"))
    interoperability = directory((0x0001, ASCII, 4, b"R98\x00"))
    thumbnail = directory(SOUND)

    result = read_exif(tiff(first, exif, gps, interoperability, thumbnail))

    assert result.get_ifd(ExifTags.IFD.GPSInfo) == {1: "N"}
    assert result.get_ifd(ExifTags.IFD.Interop) == {1: "R98"}
    assert result.get_ifd(ExifTags.IFD.IFD1) == {ORIENTATION: 6}


def test_hands_pillow_the_data_behind_one_header():
    data = tiff(directory(SOUND))

    for exif in (data, HEADER + data):
        with mock.patch.object(Image.Exif, "load") as pillow_load:
            read_exif(exif)

        pillow_load.assert_called_once_with(HEADER + data)


@pytest.mark.parametrize(
    "data",
    [
        b"not exif",
        HEADER + b"not exif",
        HEADER + HEADER + tiff(directory(SOUND)),
        b"",
        HEADER,
        b"MM\x00*",
        b"\xff\xd8\xff\xe1" + bytes(16),
        b"RIFF\x00\x00\x00\x00WEBP",
        b"MM\x00+" + tiff(directory(SOUND))[4:],
        b"II+\x00" + tiff(directory(SOUND))[4:],
    ],
)
def test_refuses_what_is_not_tiff_data(data):
    assert_refused(data)


@pytest.mark.parametrize("header", [b"II*\x00", b"II\x00*"])
def test_reads_little_endian_exif_whose_directory_is_not_at_8(header):
    data = little_endian(header)

    assert dict(read_exif(data)) == {ARTIST: "Maria"}
    assert dict(read_with_pillow_alone(keep_tags(data, [ARTIST]))) == {
        ARTIST: "Maria"
    }


def test_reads_big_endian_exif_whose_header_has_its_number_swapped():
    artist = (ARTIST, ASCII, 3, b"me\x00\x00")
    data = b"MM*\x00" + tiff(directory(SOUND, artist))[4:]

    assert dict(read_exif(data)) == {ORIENTATION: 6, ARTIST: "me"}
    assert dict(read_with_pillow_alone(keep_tags(data, [ARTIST]))) == {
        ARTIST: "me"
    }


@pytest.mark.parametrize(
    "data",
    [
        None,
        "not exif",
        PngImagePlugin.iTXt("not exif"),
        bytearray(tiff(directory(SOUND))),
        Image.Exif(),
    ],
)
def test_refuses_what_is_not_bytes(data):
    assert_refused(data)


def source_exif():
    texts = {
        MAKE: b"camera\x00",
        DATE_TIME: b"2026:11:14 10:00:00\x00",
        ARTIST: "Maria José".encode("utf-8") + b"\x00",
        COPYRIGHT: "© 2026 thumbor".encode("utf-8") + b"\x00",
    }
    first_size = 2 + 12 * (len(texts) + 3) + 4
    data_at = 8 + first_size + 18 + 18
    entries = []
    data = b""

    for tag, text in texts.items():
        offset = struct.pack(">L", data_at + len(data))
        entries.append((tag, ASCII, len(text), offset))
        data += text

    first = directory(
        *entries,
        SOUND,
        pointer(EXIF_DIRECTORY, 8 + first_size),
        pointer(GPS_DIRECTORY, 8 + first_size + 18),
    )
    exif = directory((EXIF_VERSION, UNDEFINED, 4, b"0230"))
    gps = directory((0x0001, ASCII, 2, b"N\x00\x00\x00"))

    return HEADER + tiff(first, exif, gps, data)


def test_keeps_nothing_but_the_tags_asked_for():
    source = source_exif()

    assert read_exif(source).get_ifd(ExifTags.IFD.GPSInfo) == {1: "N"}

    kept = bytes(keep_tags(source, [ARTIST, COPYRIGHT, DATE_TIME]))
    result = read_with_pillow_alone(kept)

    assert kept.startswith(HEADER)
    assert sorted(result) == [DATE_TIME, ARTIST, COPYRIGHT]
    assert result[DATE_TIME] == "2026:11:14 10:00:00"
    assert all(not directory_of(result, tag) for tag in DIRECTORIES)
    assert b"camera" not in kept


def test_keeps_the_bytes_of_a_tag_as_they_are():
    kept = bytes(keep_tags(source_exif(), [ARTIST, COPYRIGHT]))

    assert "Maria José".encode("utf-8") + b"\x00" in kept
    assert "© 2026 thumbor".encode("utf-8") + b"\x00" in kept


def test_keeps_text_of_the_utf_8_type():
    artist = "Maria José".encode("utf-8")
    data = tiff(
        directory(
            (ARTIST, UTF8, len(artist) + 1, struct.pack(">L", 8 + 30)),
            (COPYRIGHT, UTF8, 3, b"me\x00\x00"),
        ),
        artist + b"\x00",
    )

    kept = read_with_pillow_alone(keep_tags(data, [ARTIST, COPYRIGHT]))

    assert kept[ARTIST].encode("latin-1") == artist
    assert kept[COPYRIGHT] == "me"


def test_keeps_text_of_the_undefined_type():
    data = tiff(
        directory(
            (ARTIST, UNDEFINED, 6, struct.pack(">L", 8 + 30)),
            (COPYRIGHT, UNDEFINED, 3, b"me\x00\x00"),
        ),
        b"Maria\x00",
    )

    kept = read_with_pillow_alone(keep_tags(data, [ARTIST, COPYRIGHT]))

    assert dict(kept) == {ARTIST: "Maria", COPYRIGHT: "me"}


def test_keeps_the_last_of_the_tags_with_one_number():
    data = tiff(
        directory(
            (ARTIST, ASCII, 3, b"me\x00\x00"),
            (ARTIST, ASCII, 4, b"you\x00"),
        )
    )

    assert dict(read_with_pillow_alone(keep_tags(data, [ARTIST]))) == {
        ARTIST: "you"
    }


@pytest.mark.parametrize(
    "last",
    [(ARTIST, SHORT, 1, b"\x00\x06\x00\x00"), (ARTIST, ASCII, 1, bytes(4))],
)
def test_does_not_go_back_to_a_tag_that_comes_before_the_last(last):
    data = tiff(directory((ARTIST, ASCII, 3, b"me\x00\x00"), last))

    assert keep_tags(data, [ARTIST]) is None


class Measured(bytes):
    """Bytes that count how many of them have been taken in slices."""

    taken = 0

    def __getitem__(self, key):
        result = bytes.__getitem__(self, key)

        if isinstance(key, slice):
            self.taken += len(result)

        return result


def test_reads_the_text_of_a_tag_that_comes_many_times_once():
    count, size = 2000, 4000
    at = 8 + 2 + 12 * count + 4
    entry = (ARTIST, ASCII, size, struct.pack(">L", at))
    data = Measured(tiff(directory(*[entry] * count), bytes(size)))

    assert keep_tags(data, [ARTIST, COPYRIGHT, DATE_TIME]) is None
    assert size <= data.taken < 2 * len(data)


def test_keeps_both_names_of_a_copyright():
    text = b"photographer\x00editor\x00"
    data = tiff(
        directory((COPYRIGHT, ASCII, len(text), struct.pack(">L", 8 + 18))),
        text,
    )

    assert b"photographer\x00editor\x00" in bytes(keep_tags(data, [COPYRIGHT]))


def test_keeps_what_is_there_of_text_that_is_cut():
    data = tiff(
        directory((ARTIST, ASCII, 20, struct.pack(">L", 8 + 18))), b"some"
    )

    assert dict(read_with_pillow_alone(keep_tags(data, [ARTIST]))) == {
        ARTIST: "some"
    }
    assert keep_tags(data[:-4], [ARTIST]) is None


@pytest.mark.parametrize(
    "values, value, data, expected",
    [
        (4, b"you\x00", b"", "you"),
        (2, b"m\x00XY", b"", "m"),
        (5, struct.pack(">L", 8 + 18), b"four\x00", "four"),
    ],
)
def test_keeps_text_at_the_edge_of_what_fits_in_the_entry(
    values, value, data, expected
):
    exif = tiff(directory((ARTIST, ASCII, values, value)), data)

    assert dict(read_with_pillow_alone(keep_tags(exif, [ARTIST]))) == {
        ARTIST: expected
    }


def linked_exif(**moved):
    """
    A first directory and the four it leads to, one after the other, then a
    directory that is cut. A pointer goes where ``moved`` says.
    """
    at = {
        "exif": 8 + 42,
        "gps": 8 + 42 + 18,
        "interoperability": 8 + 42 + 18 + 18,
        "thumbnail": 8 + 42 + 18 + 18 + 18,
        **moved,
    }

    return tiff(
        directory(
            (ARTIST, ASCII, 3, b"me\x00\x00"),
            pointer(EXIF_DIRECTORY, at["exif"]),
            pointer(GPS_DIRECTORY, at["gps"]),
            following=at["thumbnail"],
        ),
        directory(pointer(INTEROPERABILITY_DIRECTORY, at["interoperability"])),
        directory((0x0001, ASCII, 2, b"N\x00\x00\x00")),
        directory((0x0001, ASCII, 4, b"R98\x00")),
        directory(SOUND),
        directory(SOUND)[:CUT_SIZE],
    )


CUT_SIZE = 10
CUT_AT = 8 + 42 + 18 + 18 + 18 + 18
POINTERS = ["exif", "gps", "interoperability", "thumbnail"]


def test_keeps_tags_of_exif_whose_directories_are_all_whole():
    data = linked_exif()

    assert len(data) == CUT_AT + CUT_SIZE
    assert dict(read_with_pillow_alone(keep_tags(data, [ARTIST]))) == {
        ARTIST: "me"
    }


@pytest.mark.parametrize("name", POINTERS)
@pytest.mark.parametrize(
    "offset", [CUT_AT, CUT_AT + CUT_SIZE - 1, CUT_AT + CUT_SIZE, 2**32 - 1]
)
def test_refuses_exif_that_leads_to_a_directory_that_is_not_whole(
    name, offset
):
    data = linked_exif(**{name: offset})

    with pytest.raises(ValueError):
        keep_tags(data, [ARTIST])


@pytest.mark.parametrize("name", POINTERS)
def test_takes_a_directory_that_ends_where_the_data_does(name):
    # No thumbnail, so that nothing but the pointer leads to the directory
    data = linked_exif(**{"thumbnail": 0, name: CUT_AT - 18})

    assert keep_tags(data[:CUT_AT], [ARTIST])

    # Only the first directory has to have what comes after its entries
    assert keep_tags(data[: CUT_AT - 4], [ARTIST])

    with pytest.raises(ValueError):
        keep_tags(data[: CUT_AT - 5], [ARTIST])


def test_takes_a_directory_without_entries_at_the_end_of_the_data():
    data = tiff(
        directory(
            (ARTIST, ASCII, 3, b"me\x00\x00"),
            pointer(GPS_DIRECTORY, 8 + 30),
        ),
        bytes(2),
    )

    assert keep_tags(data, [ARTIST])

    with pytest.raises(ValueError, match="outside the data"):
        keep_tags(data[:-1], [ARTIST])


@pytest.mark.parametrize(
    "data",
    [
        b"MM\x00*" + struct.pack(">L", 4096),
        b"MM\x00*" + struct.pack(">L", 8),
        b"MM\x00*" + struct.pack(">L", 8) + b"\x00",
        tiff(directory((ARTIST, ASCII, 3, b"me\x00\x00"), declared=2)),
        tiff(directory((ARTIST, ASCII, 3, b"me\x00\x00")))[:-1],
        tiff(directory((ARTIST, ASCII, 3, b"me\x00\x00")))[:-4],
        tiff(directory((ARTIST, ASCII, 3, b"me\x00\x00")))[:-5],
    ],
)
def test_refuses_exif_whose_first_directory_is_not_whole(data):
    with pytest.raises(ValueError):
        keep_tags(data, [ARTIST])


@pytest.mark.parametrize(
    "entry, data",
    [
        ((GPS_DIRECTORY, SHORT, 1, struct.pack(">L", 4096)), b""),
        ((GPS_DIRECTORY, LONG, 2, struct.pack(">L", 8 + 30)), b"\xff" * 8),
        ((GPS_DIRECTORY, ASCII, 4, struct.pack(">L", 4096)), b""),
        ((GPS_DIRECTORY, 13, 1, struct.pack(">L", 4096)), b""),
        ((INTEROPERABILITY_DIRECTORY, LONG, 1, struct.pack(">L", 4096)), b""),
    ],
)
def test_does_not_go_where_no_pointer_leads(entry, data):
    exif = tiff(directory((ARTIST, ASCII, 3, b"me\x00\x00"), entry), data)

    assert dict(read_with_pillow_alone(keep_tags(exif, [ARTIST]))) == {
        ARTIST: "me"
    }


def test_goes_where_the_last_of_the_pointers_with_one_number_leads():
    artist = (ARTIST, ASCII, 3, b"me\x00\x00")
    sound = pointer(GPS_DIRECTORY, 8 + 42)
    broken = pointer(GPS_DIRECTORY, 4096)
    gps = directory((0x0001, ASCII, 2, b"N\x00\x00\x00"))

    last_sound = tiff(directory(artist, broken, sound), gps)
    last_broken = tiff(directory(artist, sound, broken), gps)

    assert keep_tags(last_sound, [ARTIST])

    with pytest.raises(ValueError):
        keep_tags(last_broken, [ARTIST])


def exif_with_numbers(value_type, values, size, cut=0, inside="first"):
    """A tag of one of two directories, and its values after them."""
    gps_at = 8 + 42
    numbers = (
        X_RESOLUTION,
        value_type,
        values,
        struct.pack(">L", gps_at + 18),
    )
    data = tiff(
        directory(
            (ARTIST, ASCII, 3, b"me\x00\x00"),
            numbers if inside == "first" else SOUND,
            pointer(GPS_DIRECTORY, gps_at),
        ),
        directory(numbers if inside == "gps" else SOUND),
        bytes(size),
    )

    return data[: len(data) - cut]


@pytest.mark.parametrize("inside", ["first", "gps"])
@pytest.mark.parametrize(
    "value_type, unit",
    [
        (1, 1),
        (SHORT, 2),
        (LONG, 4),
        (5, 8),
        (6, 1),
        (8, 2),
        (9, 4),
        (10, 8),
        (11, 4),
        (12, 8),
    ],
)
@pytest.mark.parametrize("values", [5, 6])
def test_refuses_exif_with_numbers_outside_the_data(
    inside, value_type, unit, values
):
    size = unit * values
    sound = exif_with_numbers(value_type, values, size, inside=inside)
    cut = exif_with_numbers(value_type, values, size, cut=1, inside=inside)

    assert dict(read_with_pillow_alone(keep_tags(sound, [ARTIST]))) == {
        ARTIST: "me"
    }

    with pytest.raises(ValueError, match="numbers outside the data"):
        keep_tags(cut, [ARTIST])


@pytest.mark.parametrize(
    "value_type, values",
    [
        (1, 4),
        (SHORT, 2),
        (LONG, 1),
        (ASCII, 60),
        (UNDEFINED, 60),
        (UTF8, 60),
        (0, 60),
        (13, 15),
    ],
)
def test_takes_exif_with_no_numbers_outside_the_data(value_type, values):
    data = exif_with_numbers(value_type, values, 0)

    assert dict(read_with_pillow_alone(keep_tags(data, [ARTIST]))) == {
        ARTIST: "me"
    }


@pytest.mark.parametrize("name", EXIF_FIXTURES)
def test_takes_the_fixtures_but_the_one_with_a_directory_outside(name):
    exif = fixture_exif(name)

    if name == "broken-exif-tag.jpg":
        with pytest.raises(ValueError, match="outside the data"):
            keep_tags(exif, [ARTIST, COPYRIGHT, DATE_TIME])
    else:
        keep_tags(exif, [ARTIST, COPYRIGHT, DATE_TIME])


def test_keeps_tags_without_handing_the_exif_to_pillow():
    with mock.patch.object(Image.Exif, "load") as pillow_load:
        kept = keep_tags(source_exif(), [ARTIST, COPYRIGHT, DATE_TIME])

    pillow_load.assert_not_called()
    assert kept


def test_keeps_nothing_when_no_tag_asked_for_is_there():
    assert keep_tags(source_exif(), [0x010E]) is None
    assert keep_tags(tiff(directory(SOUND)), [ARTIST, COPYRIGHT]) is None


def test_does_not_keep_a_tag_that_is_not_text():
    data = tiff(
        directory(
            (COPYRIGHT, SHORT, 2, b"ABCD"),
            (ARTIST, ASCII, 3, b"me\x00\x00"),
        )
    )

    kept = read_with_pillow_alone(keep_tags(data, [ARTIST, COPYRIGHT]))

    assert dict(kept) == {ARTIST: "me"}
    assert keep_tags(data, [COPYRIGHT]) is None


@pytest.mark.parametrize("data", [b"not exif", "not exif", None])
def test_keeps_no_tag_of_exif_it_does_not_read(data):
    with pytest.raises(ValueError):
        keep_tags(data, [ARTIST, COPYRIGHT, DATE_TIME])
