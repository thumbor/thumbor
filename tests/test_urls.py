#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.url import Url

def test_url_generate_with_manual_crop():
    url = Url.generate_options(
        width=300,
        height=200,
        crop_left=10,
        crop_top=11,
        crop_right=12,
        crop_bottom=13
    )

    assert url == '10x11:12x13/300x200'

def test_url_generate_with_meta():
    url = Url.generate_options(
        meta=True
    )

    assert url == 'meta/0x0'

def test_default_url():
    url = Url.generate_options()
    assert url == '0x0'

def test_complete_url():
    url = Url.generate_options(
        width=300,
        height=200,
        smart=True,
        meta=True,
        horizontal_flip=True,
        vertical_flip=True,
        crop_left=10,
        crop_top=11,
        crop_right=12,
        crop_bottom=13
    )

    assert url == 'meta/10x11:12x13/-300x-200/smart', url

def test_returns_route_regex_with_default_filters():
    url = Url.regex()

    assert url == '/?unsafe/(?:(?P<meta>meta)/)?(?:(?P<crop_left>\d+)x(?P<crop_top>\d+):(?P<crop_right>\d+)x(?P<crop_bottom>\d+)/)?(?:(?P<fit_in>fit-in)/)?(?:(?P<horizontal_flip>-)?(?P<width>\d+)?x(?P<vertical_flip>-)?(?P<height>\d+)?/)?(?:(?P<halign>left|right|center)/)?(?:(?P<valign>top|bottom|middle)/)?(?:(?P<smart>smart)/)?(?P<image>.+)'

def test_returns_route_regex_with_filters():
    class TestFilter(object):
        regex = r'some-filter-fake-regex'

    url = Url.regex(filters=[TestFilter])

    assert url == '/?unsafe/(?:(?P<meta>meta)/)?(?:(?P<crop_left>\d+)x(?P<crop_top>\d+):(?P<crop_right>\d+)x(?P<crop_bottom>\d+)/)?(?:(?P<fit_in>fit-in)/)?(?:(?P<horizontal_flip>-)?(?P<width>\d+)?x(?P<vertical_flip>-)?(?P<height>\d+)?/)?(?:(?P<halign>left|right|center)/)?(?:(?P<valign>top|bottom|middle)/)?(?:(?P<smart>smart)/)?some-filter-fake-regex(?P<image>.+)'

def test_returns_route_regex_without_image():
    url = Url.regex(include_image=False)

    assert url == '/?unsafe/(?:(?P<meta>meta)/)?(?:(?P<crop_left>\d+)x(?P<crop_top>\d+):(?P<crop_right>\d+)x(?P<crop_bottom>\d+)/)?(?:(?P<fit_in>fit-in)/)?(?:(?P<horizontal_flip>-)?(?P<width>\d+)?x(?P<vertical_flip>-)?(?P<height>\d+)?/)?(?:(?P<halign>left|right|center)/)?(?:(?P<valign>top|bottom|middle)/)?(?:(?P<smart>smart)/)?'

def test_parse_urls_without_result():
    options = Url.parse_options("some fake url")

    assert not options

def test_parse_urls_without_image():

    options = Url.parse_options('unsafe/meta/10x11:12x13/-300x-200/left/top/smart/')

    assert options

    options = Url.parse_options('/unsafe/meta/10x11:12x13/-300x-200/left/top/smart/')

    assert options
    assert options['meta'] == True

    assert options['crop']['left'] == 10
    assert options['crop']['top'] == 11
    assert options['crop']['right'] == 12
    assert options['crop']['bottom'] == 13

    assert options['width'] == 300
    assert options['height'] == 200

    assert options['horizontal_flip'] == True
    assert options['vertical_flip'] == True

    assert options['halign'] == 'left'
    assert options['valign'] == 'top'

    assert options['smart'] == True

def test_parse_urls_with_image():

    image_url = 's.glbimg.com/es/ge/f/original/2011/03/29/orlandosilva_60.jpg'

    options = Url.parse('/unsafe/meta/10x11:12x13/-300x-200/left/top/smart/%s' % image_url)

    assert options['image']
    assert options['image'] == image_url

    options = Url.parse('unsafe/meta/10x11:12x13/-300x-200/left/top/smart/%s' % image_url)

    assert options['image']
    assert options['image'] == image_url

