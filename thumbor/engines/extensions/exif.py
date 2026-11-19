# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

import struct

from PIL import Image

from thumbor.engines.extensions.exif_orientation_editor import (
    EXIF_HEADER,
    PREFIXES,
)

BYTE_ORDERS = {
    prefix: "<" if prefix.startswith(b"II") else ">" for prefix in PREFIXES
}

# ASCII, UNDEFINED, whose bytes piexif kept as text, and the UTF-8 of EXIF
# 3.0, which Pillow does not read
TEXT_TYPES = (2, 7, 129)
LONG = 4
# Bytes one value of each type of number takes
NUMBER_SIZES = {1: 1, 3: 2, 4: 4, 5: 8, 6: 1, 8: 2, 9: 4, 10: 8, 11: 4, 12: 8}
ENTRY_SIZE = 12
INLINE_SIZE = 4
LINK_SIZE = 4

EXIF_DIRECTORY = 0x8769
GPS_DIRECTORY = 0x8825
INTEROPERABILITY_DIRECTORY = 0xA005


def _entries(tiff, byte_order, offset, link=False):
    """
    Returns the tag, the type, the number of values and the four bytes of
    value of each entry of the directory at an offset. Raises ValueError for
    a directory that is not whole, which takes the offset stored after the
    entries when the directory links to another.
    """
    start = offset + 2

    if start > len(tiff):
        raise ValueError("EXIF directory outside the data")

    (declared,) = struct.unpack_from(byte_order + "H", tiff, offset)
    end = start + ENTRY_SIZE * declared

    if end + (LINK_SIZE if link else 0) > len(tiff):
        raise ValueError("EXIF directory cut short")

    return [
        struct.unpack_from(byte_order + "HHL4s", tiff, position)
        for position in range(start, end, ENTRY_SIZE)
    ]


def _named(entries, byte_order, tag):
    """
    Returns the offset of the directory a tag names, or None when the tag
    is not there or is not one LONG. Of a tag that comes more than once,
    the last one counts.
    """
    pointers = [entry for entry in entries if entry[0] == tag]

    if not pointers or pointers[-1][1:3] != (LONG, 1):
        return None

    return struct.unpack(byte_order + "L", pointers[-1][3])[0]


def _directories(tiff, byte_order, first):
    """
    Returns the entries of the first directory and of the ones it leads to:
    the Exif one and the Interoperability one that it names, the GPS one
    and the thumbnail's. Raises ValueError when one of them is not whole.
    """
    entries = _entries(tiff, byte_order, first, link=True)
    (thumbnail,) = struct.unpack_from(
        byte_order + "L", tiff, first + 2 + ENTRY_SIZE * len(entries)
    )
    directories = [entries]
    offsets = [_named(entries, byte_order, GPS_DIRECTORY), thumbnail or None]
    details = _named(entries, byte_order, EXIF_DIRECTORY)

    if details is not None:
        directories.append(_entries(tiff, byte_order, details))
        offsets.append(
            _named(directories[-1], byte_order, INTEROPERABILITY_DIRECTORY)
        )

    directories.extend(
        _entries(tiff, byte_order, offset)
        for offset in offsets
        if offset is not None
    )

    return directories


def _sound(tiff, byte_order, first):
    """
    Returns the entries of the first directory of EXIF that is all there.
    Raises ValueError for EXIF with a directory that is not whole, or with
    a tag whose numbers lie outside the data.

    piexif, which read EXIF up to thumbor 7.8.0, failed on such EXIF, and
    the copyright option keeps whole the EXIF that cannot be read. Text that
    lies outside the data did not stop piexif, so it does not count here.
    """
    directories = _directories(tiff, byte_order, first)

    for entries in directories:
        for _, value_type, values, value in entries:
            size = values * NUMBER_SIZES.get(value_type, 0)

            if size <= INLINE_SIZE:
                continue

            (offset,) = struct.unpack(byte_order + "L", value)

            if offset + size > len(tiff):
                raise ValueError("EXIF tag with numbers outside the data")

    return directories[0]


def _check(tiff):
    """
    Refuses what is not TIFF data. Returns its byte order and the offset of
    its first directory.
    """
    byte_order = BYTE_ORDERS.get(tiff[:4])

    if byte_order is None or len(tiff) < 8:
        raise ValueError("EXIF is not TIFF data")

    (first,) = struct.unpack_from(byte_order + "L", tiff, 4)

    return byte_order, first


def _checked(exif):
    """
    Returns the TIFF data of EXIF, without the header it may come with, its
    byte order and the offset of its first directory. Raises ValueError for
    EXIF that is not TIFF data.

    The EXIF of some formats reaches thumbor exactly as the image has it,
    which may be text or anything else, so only TIFF data is read.
    """
    if not isinstance(exif, bytes):
        raise ValueError("EXIF is not bytes")

    tiff = exif[len(EXIF_HEADER) :] if exif.startswith(EXIF_HEADER) else exif

    return (tiff, *_check(tiff))


def read_exif(exif):
    """
    Reads EXIF with Pillow. Raises ValueError when it is not TIFF data.
    """
    tiff, _, _ = _checked(exif)
    result = Image.Exif()
    result.load(EXIF_HEADER + tiff)

    return result


def keep_tags(exif, tags):
    """
    Returns EXIF with nothing but the given text tags of the first
    directory, with the bytes they have, or None when the EXIF has none of
    them. Of a tag that comes more than once, the last one counts. Raises
    ValueError for EXIF that is not TIFF data, and for EXIF that is not all
    there.
    """
    tiff, byte_order, first = _checked(exif)
    entries = {
        entry[0]: entry[1:] for entry in _sound(tiff, byte_order, first)
    }
    kept = Image.Exif()

    for tag in tags:
        value_type, values, value = entries.get(tag, (None, 0, b""))

        if value_type not in TEXT_TYPES:
            continue

        if values > INLINE_SIZE:
            (offset,) = struct.unpack(byte_order + "L", value)
            value = tiff[offset : offset + values]

        text = value[:values].rstrip(b"\x00")

        if text:
            kept[tag] = text

    return kept.tobytes() if len(kept) else None
