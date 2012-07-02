#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import re

class Url(object):

    unsafe = r'(?P<unsafe>unsafe/)?'
    hash_regexp = r'(?:(?P<hash>[^/]{28,}?)/)?'
    debug = '(?:(?P<debug>debug)/)?'
    meta = '(?:(?P<meta>meta)/)?'
    crop = '(?:(?P<crop_left>\d+)x(?P<crop_top>\d+):(?P<crop_right>\d+)x(?P<crop_bottom>\d+)/)?'
    fit_in = '(?:(?P<adaptive>adaptive-)?(?P<fit_in>fit-in)/)?'
    dimensions = '(?:(?P<horizontal_flip>-)?(?P<width>(?:\d+|orig))?x(?P<vertical_flip>-)?(?P<height>(?:\d+|orig))?/)?'
    halign = r'(?:(?P<halign>left|right|center)/)?'
    valign = r'(?:(?P<valign>top|bottom|middle)/)?'
    smart = r'(?:(?P<smart>smart)/)?'
    filters = r'(?:filters:(?P<filters>.+\))/)?'
    image = r'(?P<image>.+)'

    compiled_regex = None

    @classmethod
    def regex(cls, old_format=False):
        reg = ['/?']

        reg.append(cls.unsafe)

        if not old_format:
            reg.append(cls.hash_regexp)

        reg.append(cls.debug)
        reg.append(cls.meta)
        reg.append(cls.crop)
        reg.append(cls.fit_in)
        reg.append(cls.dimensions)
        reg.append(cls.halign)
        reg.append(cls.valign)
        reg.append(cls.smart)
        reg.append(cls.filters)
        reg.append(cls.image)

        return ''.join(reg)

    @classmethod
    def parse(cls, url):
        if cls.compiled_regex:
            reg = cls.compiled_regex
        else:
            reg = cls.compiled_regex = re.compile(cls.regex(old_format=True))

        result = reg.match(url)

        if not result:
            return None

        result = result.groupdict()

        int_or_0 = lambda value: 0 if value is None else int(value)
        values = {
            'debug': result['debug'] == 'debug',
            'meta': result['meta'] == 'meta',
            'crop': {
                'left': int_or_0(result['crop_left']),
                'top': int_or_0(result['crop_top']),
                'right': int_or_0(result['crop_right']),
                'bottom': int_or_0(result['crop_bottom'])
            },
            'adaptive': result['adaptive'] == 'adaptive',
            'fit_in': result['fit_in'] == 'fit-in',
            'width': result['width'] == 'orig' and 'orig' or int_or_0(result['width']),
            'height': result['height'] == 'orig' and 'orig' or int_or_0(result['height']),
            'horizontal_flip': result['horizontal_flip'] == '-',
            'vertical_flip': result['vertical_flip'] == '-',
            'halign': result['halign'] or 'center',
            'valign': result['valign'] or 'middle',
            'smart': result['smart'] == 'smart',
            'filters': result['filters'] or '',
            'image': 'image' in result and result['image'] or None
        }

        return values

    @classmethod
    def generate_options(cls,
                         debug=False,
                         width=0,
                         height=0,
                         smart=False,
                         meta=False,
                         adaptive=False,
                         fit_in=False,
                         horizontal_flip=False,
                         vertical_flip=False,
                         halign='center',
                         valign='middle',
                         crop_left=None,
                         crop_top=None,
                         crop_right=None,
                         crop_bottom=None,
                         filters=None):

        url = []

        if debug:
            url.append('debug')

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
            if adaptive:
                url.append('adaptive-fit-in')
            else:
                url.append('fit-in')

        if horizontal_flip:
            width = '-%s' % width
        if vertical_flip:
            height = '-%s' % height

        if width or height:
            url.append('%sx%s' % (width, height))

        if halign != 'center':
            url.append(halign)
        if valign != 'middle':
            url.append(valign)

        if smart:
            url.append('smart')

        if filters:
            url.append('filters:%s' % filters)

        return '/'.join(url)

