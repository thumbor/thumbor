# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import unicodedata
from contextlib import contextmanager
from io import BytesIO
from os.path import exists
from unittest import mock, skipUnless

from PIL import Image

from thumbor.testing import DetectorTestCase as ThumborDetectorTestCase
from thumbor.testing import FilterTestCase as ThumborFilterTestCase
from thumbor.testing import TestCase as ThumborTestCase
from thumbor.testing import get_ssim

try:
    from PIL import _avif  # noqa pylint: disable=ungrouped-imports
except ImportError:
    try:
        from pillow_avif import _avif
    except ImportError:
        _avif = None

try:
    from pillow_heif import HeifImagePlugin
except ImportError:
    HeifImagePlugin = None

try:
    import pillow_jxl  # noqa pylint: disable=unused-import
except ImportError:
    pass

AVIF_AVAILABLE = _avif is not None
HEIF_AVAILABLE = HeifImagePlugin is not None
JXL_AVAILABLE = "JXL" in Image.OPEN and "JXL" in Image.SAVE

skip_unless_avif = skipUnless(
    AVIF_AVAILABLE,
    "AVIF format support not found. Skipping AVIF tests.",
)

skip_unless_heif = skipUnless(
    HEIF_AVAILABLE,
    "HEIF format support not found. Skipping HEIF tests.",
)

skip_unless_jxl = skipUnless(
    JXL_AVAILABLE,
    "JPEG XL format support not found. Skipping JPEG XL tests.",
)


@contextmanager
def pillow_formats(opener=None, saver=None):
    """
    Lets a test give Pillow a JPEG XL opener or saver of its own, or none
    when the argument is None, and puts the registries back afterwards.
    """
    # Pillow registers its plugins the first time it needs them. One that
    # registered inside the patches would be forgotten when they end.
    Image.init()
    formats = [name for name in Image.ID if name != "JXL"]

    with (
        mock.patch.dict(Image.OPEN),
        mock.patch.dict(Image.SAVE),
        mock.patch.object(Image, "ID", formats),
    ):
        Image.OPEN.pop("JXL", None)
        Image.SAVE.pop("JXL", None)

        if opener is not None:
            Image.OPEN["JXL"] = opener
            Image.ID.append("JXL")

        if saver is not None:
            Image.SAVE["JXL"] = saver

        yield


def skip_unless_avif_encoder(codec_name):
    return skipUnless(
        _avif and _avif.encoder_codec_available(codec_name),
        f"{codec_name} encode not available",
    )


class TestCase(ThumborTestCase):
    pass


class DetectorTestCase(ThumborDetectorTestCase):
    pass


class FilterTestCase(ThumborFilterTestCase):
    pass


def assert_exists(path):
    assert exists(path), f"Expected path to exist: {path}"


def normalize_unicode_path(path):
    normalized_path = path
    for unicode_format in ["NFD", "NFC", "NFKD", "NFKC"]:
        normalized_path = unicodedata.normalize(unicode_format, str(path))
        if exists(normalized_path):
            break
    return normalized_path


def assert_same_as(topic, expected):
    topic = normalize_unicode_path(topic)
    expected = normalize_unicode_path(expected)

    if not exists(topic):
        raise AssertionError(f"File at {topic} does not exist")
    if not exists(expected):
        raise AssertionError(f"File at {expected} does not exist")

    topic_image = Image.open(topic)
    expected_image = Image.open(expected)

    assert get_ssim(topic_image, expected_image) > 0.95


def assert_similar_to(topic, expected):
    topic_image = Image.open(BytesIO(topic))
    expected_image = Image.open(BytesIO(expected))

    assert get_ssim(topic_image, expected_image) > 0.95


def assert_is_webp(data):
    image = Image.open(BytesIO(data))
    assert image.format.lower() == "webp"


def assert_is_avif(data):
    image = Image.open(BytesIO(data))
    assert image.format.lower() == "avif"


def assert_is_heif(data):
    image = Image.open(BytesIO(data))
    assert image.format.lower() == "heif"


def assert_is_png(data):
    image = Image.open(BytesIO(data))
    assert image.format.lower() == "png"


def assert_is_gif(data):
    image = Image.open(BytesIO(data))
    assert image.format.lower() == "gif"


def assert_is_jpeg(data):
    image = Image.open(BytesIO(data))
    assert image.format.lower() == "jpeg"


def assert_is_resized(image):
    assert image.has_resized_properly()


def assert_is_cropped(image):
    assert image.has_cropped_properly()
