#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com


from os.path import abspath, join, dirname


##
# Images used for tests :
#   - valid image      : JPEG 620x465, 69.88 KB
#   - too small image  : JPEG 20x20, 822 B
#   - too weight image : JPEG 300x400, 85.32 KB
##
valid_image_path = abspath(join(dirname(__file__), u'alabama1_ap620é.jpg'))
too_small_image_path = abspath(join(dirname(__file__), 'crocodile.jpg'))
too_heavy_image_path = abspath(join(dirname(__file__), 'conselheira_tutelar.jpg'))


def valid_image():
    with open(valid_image_path, 'r') as stream:
        body = stream.read()
    return body


def too_small_image():
    with open(too_small_image_path, 'r') as stream:
        body = stream.read()
    return body


def too_heavy_image():
    with open(too_heavy_image_path, 'r') as stream:
        body = stream.read()
    return body
