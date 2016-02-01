#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import re
from urllib import quote, unquote


class Url(object):

    unsafe_or_hash = r'(?:(?:(?P<unsafe>unsafe)|(?P<hash>.+?))/)?'
    debug = '(?:(?P<debug>debug)/)?'
    meta = '(?:(?P<meta>meta)/)?'
    trim = '(?:(?P<trim>trim(?::(?:top-left|bottom-right))?(?::\d+)?)/)?'
    crop = '(?:(?P<crop_left>\d+)x(?P<crop_top>\d+):(?P<crop_right>\d+)x(?P<crop_bottom>\d+)/)?'
    fit_in = '(?:(?P<adaptive>adaptive-)?(?P<full>full-)?(?P<fit_in>fit-in)/)?'
    dimensions = '(?:(?P<horizontal_flip>-)?(?P<width>(?:\d+|orig))?x(?P<vertical_flip>-)?(?P<height>(?:\d+|orig))?/)?'
    halign = r'(?:(?P<halign>left|right|center)/)?'
    valign = r'(?:(?P<valign>top|bottom|middle)/)?'
    smart = r'(?:(?P<smart>smart)/)?'
    # allow trailing ) or url-encoded %29 since tornado apparently doesn't unescape this at the point where it
    # matches the regex. This allows bad clients and proxies that re-encode extra chars to still pass security
    # see https://github.com/thumbor/thumbor/issues/598
    filters = r'(?:filters:(?P<filters>.+?(?:\)|%29))/)?'
    image = r'(?P<image>.+)'

    compiled_regex = None

    @classmethod
    def regex(cls, has_unsafe_or_hash=True):
        reg = ['/?']

        if has_unsafe_or_hash:
            reg.append(cls.unsafe_or_hash)
        reg.append(cls.debug)
        reg.append(cls.meta)
        reg.append(cls.trim)
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
    def parse_decrypted(cls, url):
        if cls.compiled_regex:
            reg = cls.compiled_regex
        else:
            reg = cls.compiled_regex = re.compile(cls.regex(has_unsafe_or_hash=False))

        result = reg.match(url)

        if not result:
            return None

        result = result.groupdict()

        int_or_0 = lambda value: 0 if value is None else int(value)

        adaptive = (result.get('adaptive', '') or '').startswith('adaptive')
        full = (result.get('full', '') or '').startswith('full')

        values = {
            'debug': result['debug'] == 'debug',
            'meta': result['meta'] == 'meta',
            'trim': result['trim'],
            'crop': {
                'left': int_or_0(result['crop_left']),
                'top': int_or_0(result['crop_top']),
                'right': int_or_0(result['crop_right']),
                'bottom': int_or_0(result['crop_bottom'])
            },
            'adaptive': adaptive,
            'full': full,
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

    @classmethod  # NOQA
    def generate_options(cls,
                         debug=False,
                         width=0,
                         height=0,
                         smart=False,
                         meta=False,
                         trim=None,
                         adaptive=False,
                         full=False,
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

        if trim:
            if isinstance(trim, bool):
                url.append('trim')
            else:
                url.append('trim:%s' % trim)

        crop = crop_left or crop_top or crop_right or crop_bottom
        if crop:
            url.append('%sx%s:%sx%s' % (
                crop_left,
                crop_top,
                crop_right,
                crop_bottom
            ))

        if fit_in:
            fit_ops = []
            if adaptive:
                fit_ops.append('adaptive')
            if full:
                fit_ops.append('full')
            fit_ops.append('fit-in')
            url.append('-'.join(fit_ops))

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

    @classmethod
    def encode_url(kls, url):
        return quote(url, '/:?%=&()~",\'$')

    @classmethod
    def reencode_url(kls, url):
        '''
        Takes the raw URL and decodes any percent encoded characters that occur before the
        source URL starts. We then re-encode the URL using encode_url which has a custom whitelist
        of chars to leave unencoded (the same ones presumably used while generating URL in first place).

        This is to work around clients that add additional encoding to thumbor URLs (for example percent
        encoding the parentheses in filter strings) which cause original security hash to be invalidated.

        By decoding and re-encoding with our permissive list, we should recover
        the original URL to validate, even if clients added additional encoding in the process.

        We leave the source URL alone as that may have legitimately contained other percent encoded chars.

        This does make this only a partial solution - if source URL had unescaped chars like parens that
        were escaped further by a bad client, the hash will still not match... But clients should be able to
        fix that by escaping all special chars in the source URL in the first place.

        See https://github.com/thumbor/thumbor/issues/598
        '''
        last_slash = url.rfind('/')
        if last_slash > 0:
            url = unquote(url[0:last_slash]) + url[last_slash:]

        return url
