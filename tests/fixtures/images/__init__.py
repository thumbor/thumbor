#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import unicodedata
from os import listdir
from os.path import abspath, join, dirname


##
# Images used for tests :
#   - valid image      : JPEG 620x465, 69.88 KB
#   - too small image  : JPEG 20x20, 822 B
#   - too weight image : JPEG 300x400, 85.32 KB
##
def get_abs_path(img):
    return abspath(join(dirname(__file__), img))

valid_image_path = get_abs_path(u'alabama1_ap620é.jpg')
too_small_image_path = get_abs_path(u'crocodile.jpg')
too_heavy_image_path = get_abs_path(u'conselheira_tutelar.jpg')
default_image_path = get_abs_path(u'image.jpg')
alabama1_image_path = get_abs_path(u'alabama1_ap620%C3%A9.jpg')
space_image_path = get_abs_path(u'image%20space.jpg')
invalid_quantization_image_path = get_abs_path(u'invalid_quantization.jpg')
animated_image_path = get_abs_path(u'animated_image.gif')
not_so_animated_image_path = get_abs_path(u'not_so_animated_image.gif')


def get_image(img):
    encode_formats = ['NFD', 'NFC', 'NFKD', 'NFKC']
    for format in encode_formats:
        try:
            with open(unicodedata.normalize(format, img), 'r') as stream:
                body = stream.read()
                break
        except IOError:
            pass
    else:
        raise IOError('%s not found' % img)
    return body


def valid_image():
    return get_image(valid_image_path)


def too_small_image():
    return get_image(too_small_image_path)


def too_heavy_image():
    return get_image(too_heavy_image_path)


def default_image():
    return get_image(default_image_path)


def alabama1():
    return get_image(alabama1_image_path)


def space_image():
    return get_image(space_image_path)


def invalid_quantization():
    return get_image(invalid_quantization_image_path)


def animated_image():
    return get_image(animated_image_path)


def not_so_animated_image():
    return get_image(not_so_animated_image_path)
