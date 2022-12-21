#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import unicodedata
from io import BytesIO
from os.path import exists
from unittest import skipUnless

from PIL import Image
from preggy import create_assertions

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

AVIF_AVAILABLE = _avif is not None
HEIF_AVAILABLE = HeifImagePlugin is not None

skip_unless_avif = skipUnless(
    AVIF_AVAILABLE,
    "AVIF format support not found. Skipping AVIF tests.",
)

skip_unless_heif = skipUnless(
    HEIF_AVAILABLE,
    "HEIF format support not found. Skipping HEIF tests.",
)


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


@create_assertions
def to_exist(topic):
    return exists(topic)


def normalize_unicode_path(path):
    normalized_path = path
    for unicode_format in ["NFD", "NFC", "NFKD", "NFKC"]:
        normalized_path = unicodedata.normalize(unicode_format, str(path))
        if exists(normalized_path):
            break
    return normalized_path


@create_assertions
def to_be_the_same_as(topic, expected):
    topic = normalize_unicode_path(topic)
    expected = normalize_unicode_path(expected)

    if not exists(topic):
        raise AssertionError(f"File at {topic} does not exist")
    if not exists(expected):
        raise AssertionError(f"File at {expected} does not exist")

    topic_image = Image.open(topic)
    expected_image = Image.open(expected)

    return get_ssim(topic_image, expected_image) > 0.95


@create_assertions
def to_be_similar_to(topic, expected):
    topic_image = Image.open(BytesIO(topic))
    expected_image = Image.open(BytesIO(expected))

    return get_ssim(topic_image, expected_image) > 0.95


@create_assertions
def to_be_webp(topic):
    image = Image.open(BytesIO(topic))
    return image.format.lower() == "webp"


@create_assertions
def to_be_avif(topic):
    image = Image.open(BytesIO(topic))
    return image.format.lower() == "avif"


@create_assertions
def to_be_heif(topic):
    image = Image.open(BytesIO(topic))
    return image.format.lower() == "heif"


@create_assertions
def to_be_png(topic):
    image = Image.open(BytesIO(topic))
    return image.format.lower() == "png"


@create_assertions
def to_be_gif(topic):
    image = Image.open(BytesIO(topic))
    return image.format.lower() == "gif"


@create_assertions
def to_be_jpeg(topic):
    image = Image.open(BytesIO(topic))
    return image.format.lower() == "jpeg"


@create_assertions
def to_be_resized(image):
    return image.has_resized_properly()


@create_assertions
def to_be_cropped(image):
    return image.has_cropped_properly()
