#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import re

class Url(object):

    meta = '(?:(?P<meta>meta)/)?'
    crop = '(?:(?P<crop_left>\d+)x(?P<crop_top>\d+):(?P<crop_right>\d+)x(?P<crop_bottom>\d+)/)?'
    dimensions = '(?:(?P<horizontal_flip>-)?(?P<width>\d+)?x(?P<vertical_flip>-)?(?P<height>\d+)?/)?'
    halign = r'(?:(?P<halign>left|right|center)/)?'
    valign = r'(?:(?P<valign>top|bottom|middle)/)?'
    smart = r'(?:(?P<smart>smart)/)?'
    image = r'(?P<image>.+)'

    @classmethod
    def regex(cls, include_image=True):
        reg = ['/']
        reg.append(cls.meta)
        reg.append(cls.crop)
        reg.append(cls.dimensions)
        reg.append(cls.halign)
        reg.append(cls.valign)
        reg.append(cls.smart)

        if include_image:
            reg.append(cls.image)

        return "".join(reg)

    @classmethod
    def parse_options(cls, url):
        return cls.parse(url, include_image=False)

    @classmethod
    def parse(cls, url, include_image=True):
        reg = cls.regex(include_image)

        result = re.match(reg, url)

        if not result:
            return None

        result = result.groupdict()

        int_or_0 = lambda value: 0 if value is None else int(value)
        values = {
            'meta': result['meta'] == "meta",
            'crop': {
                'left': int_or_0(result['crop_left']),
                'top': int_or_0(result['crop_top']),
                'right': int_or_0(result['crop_right']),
                'bottom': int_or_0(result['crop_bottom'])
            },
            'width': int_or_0(result['width']),
            'height': int_or_0(result['height']),
            'horizontal_flip': result['horizontal_flip'] == '-',
            'vertical_flip': result['vertical_flip'] == '-',
            'halign': result['halign'] or "center",
            'valign': result['valign'] or "middle",
            'smart': result['smart'] == 'smart',
            'image': 'image' in result and result['image'] or None
        }

        return values

    @classmethod
    def generate_options(cls,
                         width=0,
                         height=0,
                         smart=False,
                         meta=False,
                         horizontal_flip=False,
                         vertical_flip=False,
                         halign="center",
                         valign="middle",
                         crop_left=None,
                         crop_top=None,
                         crop_right=None,
                         crop_bottom=None):

        url = ['']

        if meta:
            url.append('meta')

        if crop_left is not None \
           and crop_top is not None \
           and crop_right is not None \
           and crop_bottom is not None:
            url.append('%sx%s:%sx%s' % (
                crop_left,
                crop_top,
                crop_right,
                crop_bottom
            ))

        if horizontal_flip:
            width = width * -1
        if vertical_flip:
            height = height * -1

        url.append('%sx%s' % (width, height))

        if halign != 'center':
            url.append(halign)
        if valign != 'middle':
            url.append(valign)

        if smart:
            url.append('smart')

        url.append('')

        return "/".join(url)
