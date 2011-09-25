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
    fit_in = '(?:(?P<fit_in>fit-in)/)?'
    dimensions = '(?:(?P<horizontal_flip>-)?(?P<width>\d+)?x(?P<vertical_flip>-)?(?P<height>\d+)?/)?'
    halign = r'(?:(?P<halign>left|right|center)/)?'
    valign = r'(?:(?P<valign>top|bottom|middle)/)?'
    smart = r'(?:(?P<smart>smart)/)?'
    filters = r'(?:filters:(?P<filters>.+?)/)?'
    image = r'(?P<image>.+)'

    @classmethod
    def regex(cls, with_unsafe=True, include_image=True):
        reg = ['/?']

        if with_unsafe:
            reg.append('unsafe/')

        reg.append(cls.meta)
        reg.append(cls.crop)
        reg.append(cls.fit_in)
        reg.append(cls.dimensions)
        reg.append(cls.halign)
        reg.append(cls.valign)
        reg.append(cls.smart)
        reg.append(cls.filters)

        if include_image:
            reg.append(cls.image)

        return ''.join(reg)

    @classmethod
    def parse_options(cls, url):
        return cls.parse(url, include_image=False)

    @classmethod
    def parse(cls, url, with_unsafe=True, include_image=True):
        reg = cls.regex(with_unsafe=with_unsafe,
                        include_image=include_image)

        result = re.match(reg, url)

        if not result:
            return None

        result = result.groupdict()

        int_or_0 = lambda value: 0 if value is None else int(value)
        values = {
            'meta': result['meta'] == 'meta',
            'crop': {
                'left': int_or_0(result['crop_left']),
                'top': int_or_0(result['crop_top']),
                'right': int_or_0(result['crop_right']),
                'bottom': int_or_0(result['crop_bottom'])
            },
            'fit_in': result['fit_in'] == 'fit-in',
            'width': int_or_0(result['width']),
            'height': int_or_0(result['height']),
            'horizontal_flip': result['horizontal_flip'] == '-',
            'vertical_flip': result['vertical_flip'] == '-',
            'halign': result['halign'] or 'center',
            'valign': result['valign'] or 'middle',
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
                         fit_in=False,
                         horizontal_flip=False,
                         vertical_flip=False,
                         halign='center',
                         valign='middle',
                         crop_left=None,
                         crop_top=None,
                         crop_right=None,
                         crop_bottom=None):

        url = []

        if meta:
            url.append('meta')

        crop = crop_left or crop_top or crop_right or crop_bottom
        if crop:
            url.append('%sx%s:%sx%s' % (
                crop_left,
                crop_top,
                crop_right,
                crop_bottom
            ))

        if fit_in:
            url.append('fit-in')

        if horizontal_flip:
            width = width * -1
        if vertical_flip:
            height = height * -1

        if width or height:
            url.append('%sx%s' % (width, height))

        if halign != 'center':
            url.append(halign)
        if valign != 'middle':
            url.append(valign)

        if smart:
            url.append('smart')

        return '/'.join(url)
