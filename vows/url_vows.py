#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from thumbor.url import Url


def ctx(**kw):
    class Context(Vows.Context):
        def topic(self):
            return Url.generate_options(**kw)

    return Context


@Vows.batch
class UrlVows(Vows.Context):

    class UrlGeneration(Vows.Context):

        class Default(ctx()):

            def should_return_empty_url(self, topic):
                expect(topic).to_be_empty()

        class Minimum(ctx(width=300, height=200)):

            def should_return_proper_url(self, topic):
                expect(topic).to_equal('300x200')

        class Smart(ctx(width=300, height=200, smart=True)):

            def should_return_proper_url(self, topic):
                expect(topic).to_equal('300x200/smart')

        class Debug(ctx(debug=True, smart=True)):

            def should_return_proper_url(self, topic):
                expect(topic).to_equal('debug/smart')

        class Alignments(ctx(halign='left', valign='top')):

            def should_return_proper_url(self, topic):
                expect(topic).to_equal('left/top')

        class Flipping(ctx(width=300, height=200, smart=True, horizontal_flip=True, vertical_flip=True)):

            def should_return_proper_url(self, topic):
                expect(topic).to_equal('-300x-200/smart')

        class Crop(ctx(width=300, height=200, crop_left=10, crop_top=11, crop_right=12, crop_bottom=13)):

            def should_return_proper_url(self, topic):
                expect(topic).to_equal('10x11:12x13/300x200')

        class Meta(ctx(meta=True)):

            def should_return_proper_url(self, topic):
                expect(topic).to_equal('meta')

        class FitIn(ctx(fit_in=True)):

            def should_return_proper_url(self, topic):
                expect(topic).to_equal('fit-in')

        class Filters(ctx(filters='brightness(-10):contrast(5)')):

            def should_return_proper_url(self, topic):
                expect(topic).to_equal('filters:brightness(-10):contrast(5)')

        class Adaptive(ctx(fit_in=True, adaptive=True)):

            def should_return_proper_url(self, topic):
                expect(topic).to_equal('adaptive-fit-in')

        class Full(ctx(fit_in=True, full=True)):

            def should_return_proper_url(self, topic):
                expect(topic).to_equal('full-fit-in')

        class Complete(ctx(
                width=300, height=200, smart=True, fit_in=True, meta=True, horizontal_flip=True,
                vertical_flip=True, crop_left=10, crop_top=11, crop_right=12, crop_bottom=13,
                filters="a(10):b(-10)")):

            def should_return_proper_url(self, topic):
                expect(topic).to_equal('meta/10x11:12x13/fit-in/-300x-200/smart/filters:a(10):b(-10)')

    class Regex(Vows.Context):
        def topic(self):
            return Url.regex()

        def should_contain_unsafe_or_hash(self, topic):
            expect(topic).to_include('(?:(?:(?P<unsafe>unsafe)|(?P<hash>[^/]{28,}?))/)?')

        def should_contain_meta(self, topic):
            expect(topic).to_include('(?:(?P<meta>meta)/)?')

        def should_contain_crop(self, topic):
            expect(topic).to_include('(?:(?P<crop_left>\d+)x(?P<crop_top>\d+):(?P<crop_right>\d+)x(?P<crop_bottom>\d+)/)?')

        def should_contain_fit_in(self, topic):
            expect(topic).to_include('(?:(?P<adaptive>adaptive-)?(?P<full>full-)?(?P<fit_in>fit-in)/)?')

        def should_contain_dimensions(self, topic):
            expect(topic).to_include(
                '(?:(?P<horizontal_flip>-)?(?P<width>(?:\d+|orig))?x(?P<vertical_flip>-)?(?P<height>(?:\d+|orig))?/)?')

        def should_contain_halign(self, topic):
            expect(topic).to_include('(?:(?P<halign>left|right|center)/)?')

        def should_contain_valign(self, topic):
            expect(topic).to_include('(?:(?P<valign>top|bottom|middle)/)?')

        def should_contain_smart(self, topic):
            expect(topic).to_include('(?:(?P<smart>smart)/)?')

        def should_contain_filters(self, topic):
            expect(topic).to_include('(?:filters:(?P<filters>.+?\))/)?')

        def should_contain_image(self, topic):
            expect(topic).to_include('(?P<image>.+)')

    class Parse(Vows.Context):
        class WithoutInitialSlash(Vows.Context):
            def topic(self):
                return Url.parse_decrypted('meta/10x11:12x13/-300x-200/left/top/smart/filters:some_filter()/img')

            def should_not_be_null(self, topic):
                expect(topic).not_to_be_null()

        class WithoutResult(Vows.Context):
            def topic(self):
                return Url.parse_decrypted("some fake url")

            def should_be_null(self, topic):
                expect(topic['image']).to_equal("some fake url")

        class WithoutImage(Vows.Context):
            def topic(self):
                return Url.parse_decrypted('/meta/10x11:12x13/fit-in/-300x-200/left/top/smart/filters:some_filter()/img')

            def should_have_meta(self, topic):
                expect(topic['meta']).to_be_true()

            def should_have_crop_left_of_10(self, topic):
                expect(topic['crop']['left']).to_equal(10)

            def should_have_crop_top_of_11(self, topic):
                expect(topic['crop']['top']).to_equal(11)

            def should_have_crop_right_of_12(self, topic):
                expect(topic['crop']['right']).to_equal(12)

            def should_have_crop_bottom_of_13(self, topic):
                expect(topic['crop']['bottom']).to_equal(13)

            def should_have_width_of_300(self, topic):
                expect(topic['width']).to_equal(300)

            def should_have_height_of_200(self, topic):
                expect(topic['height']).to_equal(200)

            def should_have_horizontal_flip(self, topic):
                expect(topic['horizontal_flip']).to_be_true()

            def should_have_vertical_flip(self, topic):
                expect(topic['vertical_flip']).to_be_true()

            def should_have_halign_of_left(self, topic):
                expect(topic['halign']).to_equal('left')

            def should_have_valign_of_top(self, topic):
                expect(topic['valign']).to_equal('top')

            def should_have_smart(self, topic):
                expect(topic['smart']).to_be_true()

            def should_have_fit_in(self, topic):
                expect(topic['fit_in']).to_be_true()

            def should_have_filters(self, topic):
                expect(topic['filters']).to_equal('some_filter()')

        class WithImage(Vows.Context):
            def topic(self):
                image_url = 's.glbimg.com/es/ge/f/original/2011/03/29/orlandosilva_60.jpg'

                return Url.parse_decrypted('/meta/10x11:12x13/-300x-200/left/top/smart/%s' % image_url)

            def should_have_image(self, topic):
                expect(topic).to_include('image')

            def should_have_image_like_url(self, topic):
                image_url = 's.glbimg.com/es/ge/f/original/2011/03/29/orlandosilva_60.jpg'
                expect(topic['image']).to_equal(image_url)

        class WithUrlInFilter(Vows.Context):
            def topic(self):
                return Url.parse_decrypted(
                    '/filters:watermark(s.glbimg.com/es/ge/f/original/2011/03/29/orlandosilva_60.jpg,0,0,0)/img')

            def should_have_image(self, topic):
                expect(topic['image']).to_equal('img')

            def should_have_filters(self, topic):
                expect(topic['filters']).to_equal('watermark(s.glbimg.com/es/ge/f/original/2011/03/29/orlandosilva_60.jpg,0,0,0)')

        class WithMultipleFilters(Vows.Context):
            def topic(self):
                return Url.parse_decrypted(
                    '/filters:watermark(s.glbimg.com/es/ge/f/original/2011/03/29/orlandosilva_60.jpg,0,0,0):brightness(-50):grayscale()/img')

            def should_have_image(self, topic):
                expect(topic['image']).to_equal('img')

            def should_have_filters(self, topic):
                expect(topic['filters']).to_equal('watermark(s.glbimg.com/es/ge/f/original/2011/03/29/orlandosilva_60.jpg,0,0,0):brightness(-50):grayscale()')

        class WithThumborOfThumbor(Vows.Context):
            def topic(self):
                return Url.parse_decrypted(
                    '/90x100/my.image.path/unsafe/filters:watermark(s.glbimg.com/some/image.jpg,0,0,0)/some.domain/img/path/img.jpg')

            def should_have_image(self, topic):
                expect(topic['image']).to_equal('my.image.path/unsafe/filters:watermark(s.glbimg.com/some/image.jpg,0,0,0)/some.domain/img/path/img.jpg')

            def should_have_size(self, topic):
                expect(topic['width']).to_equal(90)
                expect(topic['height']).to_equal(100)

        class WithThumborOfThumborWithFilters(Vows.Context):
            def topic(self):
                return Url.parse_decrypted(
                    '/90x100/filters:brightness(-50):contrast(20)/my.image.path/unsafe/filters:watermark(s.glbimg.com/some/image.jpg,0,0,0)/some.domain/img/path/img.jpg')

            def should_have_image(self, topic):
                expect(topic['image']).to_equal('my.image.path/unsafe/filters:watermark(s.glbimg.com/some/image.jpg,0,0,0)/some.domain/img/path/img.jpg')

            def should_have_filters(self, topic):
                expect(topic['filters']).to_equal('brightness(-50):contrast(20)')

            def should_have_size(self, topic):
                expect(topic['width']).to_equal(90)
                expect(topic['height']).to_equal(100)
