#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from unittest import TestCase

from preggy import expect

from thumbor.url import Url


class UrlTestCase(TestCase):
    def setUp(self):
        Url.compiled_regex = None

    def test_can_get_regex(self):
        regex = Url.regex()

        expect(regex).to_equal(
            '/?(?:(?:(?P<unsafe>unsafe)|(?P<hash>.+?))/)?(?:(?P<debug>debug)/)?(?:(?P<meta>meta)/)?'
            '(?:(?P<trim>trim(?::(?:top-left|bottom-right))?(?::\\d+)?)/)?'
            '(?:(?P<crop_left>\\d+)x(?P<crop_top>\\d+):(?P<crop_right>\\d+)x(?P<crop_bottom>\\d+)/)?'
            '(?:(?P<adaptive>adaptive-)?(?P<full>full-)?(?P<fit_in>fit-in)/)?(?:(?P<horizontal_flip>-)?'
            '(?P<width>(?:\\d+|orig))?x(?P<vertical_flip>-)?(?P<height>(?:\\d+|orig))?/)?'
            '(?:(?P<halign>left|right|center)/)?(?:(?P<valign>top|bottom|middle)/)?'
            '(?:(?P<smart>smart)/)?(?:filters:(?P<filters>.+?\\))/)?(?P<image>.+)'
        )

    def test_can_get_regex_without_unsafe(self):
        regex = Url.regex(False)

        expect(regex).to_equal(
            '/?(?:(?P<debug>debug)/)?(?:(?P<meta>meta)/)?'
            '(?:(?P<trim>trim(?::(?:top-left|bottom-right))?(?::\\d+)?)/)?'
            '(?:(?P<crop_left>\\d+)x(?P<crop_top>\\d+):(?P<crop_right>\\d+)x(?P<crop_bottom>\\d+)/)?'
            '(?:(?P<adaptive>adaptive-)?(?P<full>full-)?(?P<fit_in>fit-in)/)?(?:(?P<horizontal_flip>-)?'
            '(?P<width>(?:\\d+|orig))?x(?P<vertical_flip>-)?(?P<height>(?:\\d+|orig))?/)?'
            '(?:(?P<halign>left|right|center)/)?(?:(?P<valign>top|bottom|middle)/)?'
            '(?:(?P<smart>smart)/)?(?:filters:(?P<filters>.+?\\))/)?(?P<image>.+)'
        )

    def test_parsing_invalid_url(self):
        expect(Url.compiled_regex).to_be_null()

        url = ""
        expect(Url.parse_decrypted(url)).to_be_null()

    def test_parsing_complete_url(self):
        url = '/debug/meta/trim/300x200:400x500/adaptive-full-fit-in/-300x-400/' \
            'left/top/smart/filters:brightness(100)/some/image.jpg'

        expected = {
            'trim': 'trim',
            'full': True,
            'halign': 'left',
            'fit_in': True,
            'vertical_flip': True,
            'image': 'some/image.jpg',
            'crop': {'top': 200, 'right': 400, 'bottom': 500, 'left': 300},
            'height': 400,
            'width': 300,
            'meta': True,
            'horizontal_flip': True,
            'filters': 'brightness(100)',
            'valign': 'top',
            'debug': True,
            'adaptive': True,
            'smart': True,
        }

        result = Url.parse_decrypted(url)
        expect(result).not_to_be_null()
        expect(result).to_be_like(expected)

        # do it again to use compiled regex
        result = Url.parse_decrypted(url)
        expect(result).not_to_be_null()
        expect(result).to_be_like(expected)

    def test_can_generate_url(self):
        url = Url.generate_options(
            debug=True,
            width=300,
            height=200,
            smart=True,
            meta=True,
            trim=True,
            adaptive=True,
            full=True,
            fit_in=True,
            horizontal_flip=True,
            vertical_flip=True,
            halign='left',
            valign='top',
            crop_left=100,
            crop_top=100,
            crop_right=400,
            crop_bottom=400,
            filters='brightness(100)'
        )

        expect(url).to_equal(
            'debug/meta/trim/100x100:400x400/adaptive-full-fit-in/-300x-200/left/top/smart/filters:brightness(100)'
        )

    def test_can_generate_url_with_defaults(self):
        url = Url.generate_options()

        expect(url).to_be_empty()

    def test_can_generate_url_with_fitin(self):
        url = Url.generate_options(fit_in=True, adaptive=False, full=False)

        expect(url).to_equal('fit-in')

    def test_can_generate_url_with_custom_trim(self):
        url = Url.generate_options(
            debug=True,
            width=300,
            height=200,
            smart=True,
            meta=True,
            trim='300x200',
            adaptive=True,
            full=True,
            fit_in=True,
            horizontal_flip=True,
            vertical_flip=True,
            halign='left',
            valign='top',
            crop_left=100,
            crop_top=100,
            crop_right=400,
            crop_bottom=400,
            filters='brightness(100)'
        )

        expect(url).to_equal(
            'debug/meta/trim:300x200/100x100:400x400/adaptive-full-fit-in/-300x-200/left/top/smart/filters:brightness(100)'
        )

    def test_can_encode_url(self):
        url = '/tes+ t:?%=&()~",\'$'

        expect(Url.encode_url(url)).to_equal('/tes%2B%20t:?%=&()~",\'$')
