#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com


BASE_IMAGE_URL = 'my.domain.com/some/image/url.jpg'
BASE_IMAGE_MD5 = 'f33af67e41168e80fcc5b00f8bd8061a'

BASE_PARAMS = {
    'width': 0,
    'height': 0,
    'smart': False,
    'adaptive': False,
    'full': False,
    'fit_in': False,
    'flip_horizontal': False,
    'flip_vertical': False,
    'halign': 'center',
    'valign': 'middle',
    'trim': '',
    'crop_left': 0,
    'crop_top': 0,
    'crop_right': 0,
    'crop_bottom': 0,
    'filters': '',
    'image': ''
}

DECRYPT_TESTS = [
    {
        'params': {
            'width': 300, 'height': 200, 'image': BASE_IMAGE_URL
        },
        'result': {
            "horizontal_flip": False,
            "vertical_flip": False,
            "smart": False,
            "meta": False,
            "fit_in": False,
            "crop": {
                "left": 0,
                "top": 0,
                "right": 0,
                "bottom": 0
            },
            "valign": 'middle',
            "halign": 'center',
            "image_hash": BASE_IMAGE_MD5,
            "width": 300,
            "height": 200,
            'filters': '',
            'debug': False,
            'adaptive': False,
            'full': False,
            'trim': None
        }
    },
    {
        'params': {
            'filters': "quality(20):brightness(10)",
            'image': BASE_IMAGE_URL
        },
        'result': {
            "horizontal_flip": False,
            "vertical_flip": False,
            "smart": False,
            "meta": False,
            "fit_in": False,
            "crop": {
                "left": 0,
                "top": 0,
                "right": 0,
                "bottom": 0
            },
            "valign": 'middle',
            "halign": 'center',
            "image_hash": BASE_IMAGE_MD5,
            "width": 0,
            "height": 0,
            'filters': 'quality(20):brightness(10)',
            'debug': False,
            'adaptive': False,
            'full': False,
            'trim': None
        }
    }
]
