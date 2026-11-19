# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

import struct
from collections import namedtuple
from io import BytesIO

from PIL import Image, UnidentifiedImageError

from thumbor.engines.extensions.exif_orientation_editor import (
    EXIF_HEADER,
    ExifOrientationEditor,
)
from thumbor.utils import convert_to_srgb, renders_as_srgb

CODESTREAM_SIGNATURE = b"\xff\x0a"
CONTAINER_SIGNATURE = b"\x00\x00\x00\x0cJXL \r\n\x87\n"
TIFF_HEADERS = (b"II*\x00", b"MM\x00*")

# The fields up to the animation flag and the extra channel count take at
# most 283 bits
HEADER_BYTES = 64

LAST_PIECE = 0x80000000

# Encoders write about one piece for each 256x256 group of pixels, so this
# is room for gigapixels. A file made of empty pieces would otherwise cost
# an entry for each of them.
MAX_PIECES = 65536

ASPECT_RATIOS = {
    1: (1, 1),
    2: (12, 10),
    3: (4, 3),
    4: (3, 2),
    5: (16, 9),
    6: (5, 4),
    7: (2, 1),
}

# A 2-bit selector picks one of the four (bits to read, offset) of a field
SIZE = ((9, 1), (13, 1), (18, 1), (30, 1))
PREVIEW_SIZE_DIV8 = ((0, 16), (0, 32), (5, 1), (9, 33))
PREVIEW_SIZE = ((6, 1), (8, 65), (10, 321), (12, 1345))
TICKS_NUMERATOR = ((0, 100), (0, 1000), (10, 1), (30, 1))
TICKS_DENOMINATOR = ((0, 1), (0, 1001), (8, 1), (10, 1))
LOOPS = ((0, 0), (3, 0), (16, 0), (32, 0))
INTEGER_SAMPLE_BITS = ((0, 8), (0, 10), (0, 12), (6, 1))
FLOAT_SAMPLE_BITS = ((0, 32), (0, 16), (0, 24), (6, 1))
EXTRA_CHANNELS = ((0, 0), (0, 1), (4, 2), (12, 1))

ENCODER_MODES = ("RGB", "RGBA", "L", "LA")

# BaseHandler.get_image answers 400 to an error that carries Pillow's wording
# for an unreadable image, and 500 to any other
UNREADABLE = "cannot identify image file: JPEG XL %s (%s)"

Header = namedtuple("Header", "width height extra_channels animated")


def is_jxl(buffer):
    return buffer.startswith((CODESTREAM_SIGNATURE, CONTAINER_SIGNATURE))


def claim_only_jxl():
    # pillow-jxl-plugin claims any buffer with "JXL" from its fifth byte on,
    # which a JPEG, a WebP and others can have, and then fails to open it
    opener = Image.OPEN.get("JXL")

    if opener is not None:
        Image.register_open("JXL", opener[0], is_jxl)


class BitReader:
    def __init__(self, data):
        self.value = int.from_bytes(data, "little")
        self.length = len(data) * 8
        self.position = 0

    def bits(self, count):
        if self.position + count > self.length:
            raise ValueError("truncated header")

        value = (self.value >> self.position) & ((1 << count) - 1)
        self.position += count

        return value

    def u32(self, distributions):
        bits, offset = distributions[self.bits(2)]

        return self.bits(bits) + offset


def _boxes(buffer):
    view = memoryview(buffer)
    position = 0

    while position + 8 <= len(buffer):
        size, box_type = struct.unpack_from(">I4s", buffer, position)
        header = 8

        if size == 1:
            if position + 16 > len(buffer):
                return
            (size,) = struct.unpack_from(">Q", buffer, position + 8)
            header = 16

        if size == 0:
            size = len(buffer) - position

        if size < header:
            return

        # A box the file ends before runs to that end, as libjxl reads it,
        # and a codestream left short there is for the decoder to refuse
        yield box_type, view[position + header : position + size]

        position += size


def _add_piece(pieces, content):
    if len(content) < 4:
        raise ValueError("truncated codestream piece")

    index = struct.unpack_from(">I", content)[0] & ~LAST_PIECE

    if index in pieces:
        raise ValueError("repeated codestream piece")

    if len(pieces) == MAX_PIECES:
        raise ValueError("too many codestream pieces")

    pieces[index] = content[4:]


def _join_pieces(pieces):
    if sorted(pieces) != list(range(len(pieces))):
        raise ValueError("missing codestream piece")

    return b"".join(pieces[index] for index in range(len(pieces)))


def split_container(buffer):
    """
    Returns the codestream of a JPEG XL file and the content of its Exif box,
    None when it has none. Raises ValueError when the file does not hold one
    whole codestream.

    A container may carry the codestream in pieces, in any order, each with
    its place in a 4-byte index.
    """
    if buffer.startswith(CODESTREAM_SIGNATURE):
        return buffer, None

    if not buffer.startswith(CONTAINER_SIGNATURE):
        raise ValueError("no signature")

    codestreams = []
    pieces = {}
    exif = None

    for box_type, content in _boxes(buffer):
        if box_type == b"jxlc":
            if codestreams:
                raise ValueError("more than one codestream")

            codestreams.append(content)
        elif box_type == b"jxlp":
            _add_piece(pieces, content)
        elif box_type == b"Exif" and exif is None:
            exif = bytes(content)

    if pieces:
        codestreams.append(_join_pieces(pieces))

    if len(codestreams) != 1:
        raise ValueError("no single codestream")

    return bytes(codestreams[0]), exif


def _read_size(reader):
    small = reader.bits(1)
    height = (reader.bits(5) + 1) * 8 if small else reader.u32(SIZE)
    ratio = reader.bits(3)

    if ratio:
        numerator, denominator = ASPECT_RATIOS[ratio]

        return height * numerator // denominator, height

    width = (reader.bits(5) + 1) * 8 if small else reader.u32(SIZE)

    return width, height


def _skip_preview(reader):
    sizes = PREVIEW_SIZE_DIV8 if reader.bits(1) else PREVIEW_SIZE
    reader.u32(sizes)

    if not reader.bits(3):
        reader.u32(sizes)


def _skip_animation(reader):
    reader.u32(TICKS_NUMERATOR)
    reader.u32(TICKS_DENOMINATOR)
    reader.u32(LOOPS)
    reader.bits(1)


def _skip_bit_depth(reader):
    if reader.bits(1):
        reader.u32(FLOAT_SAMPLE_BITS)
        reader.bits(4)
    else:
        reader.u32(INTEGER_SAMPLE_BITS)


def _read_codestream_header(codestream):
    if not codestream.startswith(CODESTREAM_SIGNATURE):
        raise ValueError("no codestream")

    reader = BitReader(codestream[len(CODESTREAM_SIGNATURE) : HEADER_BYTES])
    width, height = _read_size(reader)
    animated = False

    all_default = reader.bits(1)
    if all_default:
        return Header(width, height, 0, animated)

    extra_fields = reader.bits(1)
    if extra_fields:
        reader.bits(3)  # orientation

        has_intrinsic_size = reader.bits(1)
        if has_intrinsic_size:
            _read_size(reader)

        has_preview = reader.bits(1)
        if has_preview:
            _skip_preview(reader)

        animated = bool(reader.bits(1))
        if animated:
            _skip_animation(reader)

    _skip_bit_depth(reader)
    reader.bits(1)  # modular_16_bit_buffer_sufficient

    return Header(width, height, reader.u32(EXTRA_CHANNELS), animated)


def read_header(buffer):
    """
    Returns the width, the height, the number of extra channels and whether
    it is an animation for a JPEG XL image, read from its header without
    decoding any pixel. The dimensions are the ones stored, before the
    orientation is applied. Raises ValueError when the header cannot be read.
    """
    codestream, _ = split_container(buffer)

    return _read_codestream_header(codestream)


def _exif_from_box(content):
    if content is None or len(content) < 4:
        return None

    # pillow-jxl-plugin writes the box without the offset that opens it
    if content.startswith(TIFF_HEADERS):
        return content

    # The box opens with the offset of the TIFF header in what follows
    (offset,) = struct.unpack_from(">I", content)

    return content[4 + offset :] or None


def exif_to_box(exif):
    """
    Returns EXIF data as the content of an Exif box, which opens with the
    offset of the TIFF header in what follows.
    """
    if exif.startswith(EXIF_HEADER):
        exif = exif[len(EXIF_HEADER) :]

    # pillow-jxl-plugin writes what it is handed as the whole content of the
    # box, while libjxl leaves the offset for its caller to put there
    return b"\0\0\0\0" + exif


def with_exif_header(exif):
    if not exif or exif.startswith(EXIF_HEADER):
        return exif

    return EXIF_HEADER + exif


def _normalize_exif(img):
    exif = with_exif_header(img.info.get("exif"))

    if not exif:
        return

    # The decoder already rotated the pixels to the orientation the
    # codestream stores, the one that counts in JPEG XL
    try:
        editor = ExifOrientationEditor(exif)
        editor.set_orientation(1)
        img.info["exif"] = editor.tobytes()
    except (SyntaxError, struct.error):
        del img.info["exif"]


def open_image(buffer):
    """
    Opens a JPEG XL image and decodes it. Raises DecompressionBombError,
    before anything is decoded, when the image is over Image.MAX_IMAGE_PIXELS
    and UnidentifiedImageError when it cannot be read.

    The decoder is handed the codestream alone, taken out of its container:
    it reads the bytes that were checked here, and none of the boxes, among
    them the one it would rebuild a recompressed JPEG from.
    """
    try:
        codestream, exif_box = split_container(buffer)
        header = _read_codestream_header(codestream)
    except ValueError as error:
        raise UnidentifiedImageError(UNREADABLE % ("header", error)) from error

    # Nothing tells how many frames there are before decoding them, and the
    # plugin hands back the last one, not the first
    if header.animated:
        raise UnidentifiedImageError(
            UNREADABLE % ("animation", "not supported")
        )

    # The decoder holds every extra channel as one more plane, shown or not.
    # The first one rides with the color channels, as alpha does in the
    # other formats.
    pixels = header.width * header.height * max(1, header.extra_channels)

    if Image.MAX_IMAGE_PIXELS and pixels > Image.MAX_IMAGE_PIXELS:
        raise Image.DecompressionBombError(
            f"JPEG XL image of {header.width}x{header.height} with "
            f"{header.extra_channels} extra channels holds {pixels} pixels, "
            f"over the limit of {Image.MAX_IMAGE_PIXELS}"
        )

    try:
        img = Image.open(BytesIO(codestream))
        img.load()
    except RuntimeError as error:
        raise UnidentifiedImageError(
            UNREADABLE % ("decoder", error)
        ) from error

    if img.mode == "F":
        # JPEG XL keeps float samples between 0 and 1
        img = img.point(lambda sample: sample * 255).convert("L")

    exif = _exif_from_box(exif_box)
    if exif is not None:
        img.info["exif"] = exif

    _normalize_exif(img)

    if renders_as_srgb(img.info.get("icc_profile")):
        del img.info["icc_profile"]

    return img


def can_encode():
    return "JXL" in Image.SAVE


def engine_can_encode(engine):
    # An engine written before JPEG XL support has no jxl_enabled
    jxl_enabled = getattr(engine, "jxl_enabled", None)

    return jxl_enabled is not None and jxl_enabled()


def codec_threads(threads):
    return -1 if threads is None else threads


def encoder_options(quality, effort, threads):
    # The plugin writes the EXIF of the image unless it is handed one
    options = {"exif": b"", "num_threads": codec_threads(threads)}

    if effort is not None:
        options["effort"] = effort

    if quality != "keep":
        if quality >= 100:
            options["lossless"] = True
        else:
            options["quality"] = quality

    return options


def prepare_image(img, icc_profile, srgb_profile):
    """
    Returns the image in a mode the encoder takes and in sRGB, since the
    encoder writes no ICC profile.
    """
    if img.mode == "I;16":
        # The plugin writes 16-bit samples as linear light, and Pillow clips
        # them when it converts to 8 bits
        img = img.convert("I").point(lambda sample: sample / 257).convert("L")
    elif img.mode == "F":
        img = img.convert("L")
    elif img.mode not in ENCODER_MODES + ("CMYK",):
        img = img.convert("RGBA" if img.has_transparency_data else "RGB")

    if icc_profile is not None:
        srgb_img = convert_to_srgb(img, icc_profile, srgb_profile)

        if srgb_img is not None:
            img = srgb_img

        img.info.pop("icc_profile", None)

    if img.mode == "CMYK":
        img = img.convert("RGB")

    return img
