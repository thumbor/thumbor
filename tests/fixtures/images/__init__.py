#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import unicodedata
from os.path import abspath, dirname, join


##
# Images used for tests :
#   - valid image      : JPEG 620x465, 69.88 KB
#   - too small image  : JPEG 20x20, 822 B
#   - too weight image : JPEG 300x400, 85.32 KB
##
def get_abs_path(img):
    return abspath(join(dirname(__file__), img))


VALID_IMAGE_PATH = get_abs_path("alabama1_ap620é.jpg")
SVG_IMAGE_PATH = get_abs_path("Commons-logo.svg")
TOO_SMALL_IMAGE_PATH = get_abs_path("20x20.jpg")
TOO_HEAVY_IMAGE_PATH = get_abs_path("Giunchedi%2C_Filippo_January_2015_01.jpg")
DEFAULT_IMAGE_PATH = get_abs_path("image.jpg")
ALABAMA1_IMAGE_PATH = get_abs_path("alabama1_ap620%C3%A9.jpg")
SPACE_IMAGE_PATH = get_abs_path("image%20space.jpg")
INVALID_QUANTIZATION_IMAGE_PATH = get_abs_path("invalid_quantization.jpg")
ANIMATED_IMAGE_PATH = get_abs_path("animated.gif")
NOT_SO_ANIMATED_IMAGE_PATH = get_abs_path("animated-one-frame.gif")


def get_image(img):
    encode_formats = ["NFD", "NFC", "NFKD", "NFKC"]
    for encode_format in encode_formats:
        try:
            with open(
                unicodedata.normalize(encode_format, img), "rb"
            ) as stream:
                body = stream.read()
                break
        except IOError:
            pass
    else:
        raise IOError(f"{img} not found")
    return body


def valid_image():
    return get_image(VALID_IMAGE_PATH)


def svg_image():
    return get_image(SVG_IMAGE_PATH)


def too_small_image():
    return get_image(TOO_SMALL_IMAGE_PATH)


def too_heavy_image():
    return get_image(TOO_HEAVY_IMAGE_PATH)


def default_image():
    return get_image(DEFAULT_IMAGE_PATH)


def alabama1():
    return get_image(ALABAMA1_IMAGE_PATH)


def space_image():
    return get_image(SPACE_IMAGE_PATH)


def invalid_quantization():
    return get_image(INVALID_QUANTIZATION_IMAGE_PATH)


def animated_image():
    return get_image(ANIMATED_IMAGE_PATH)


def not_so_animated_image():
    return get_image(NOT_SO_ANIMATED_IMAGE_PATH)
