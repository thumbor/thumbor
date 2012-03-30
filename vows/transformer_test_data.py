#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.point import FocalPoint as fp
from thumbor.context import Context, RequestParameters
from thumbor.importer import Importer

class MockEngine(object):
    def __init__(self, size):
        self.size = size
        self.calls = {
            'resize': [],
            'crop': [],
            'vertical_flip': 0,
            'horizontal_flip': 0
        }
        self.focal_points = None

    def resize(self, width, height):
        self.calls['resize'].append({
            'width': width,
            'height': height
        })

    def crop(self, left, top, right, bottom):
        self.calls['crop'].append({
            'left': left,
            'top': top,
            'right': right,
            'bottom': bottom
        })

    def flip_horizontally(self):
        self.calls['horizontal_flip'] += 1

    def flip_vertically(self):
        self.calls['vertical_flip'] += 1

    def get_proportional_width(self, new_height):
        width, height = self.size
        return float(new_height) * width / height

    def get_proportional_height(self, new_width):
        width, height = self.size
        return float(new_width) * height / width

    def focus(self, focal_points):
        self.focal_points = focal_points

class TestData(object):
    def __init__(self,
            source_width, source_height,
            target_width, target_height,
            halign, valign, focal_points,
            crop_left, crop_top, crop_right, crop_bottom,
            fit_in=False, adaptive=False):
        self.source_width = source_width
        self.source_height = source_height
        self.target_width = target_width
        self.target_height = target_height
        self.halign = halign
        self.valign = valign
        self.focal_points = focal_points
        self.crop_left = crop_left
        self.crop_top = crop_top
        self.crop_right = crop_right
        self.crop_bottom = crop_bottom
        self.fit_in = fit_in
        self.adaptive = adaptive

    def __repr__(self):
        return self.__str__()
    def __unicode__(self):
        return self.__str__()
    def __str__(self):
        crop_message = ""
        if self.crop_left is not None:
            crop_message = "it should crop %dx%d-%dx%d and " % (
                self.crop_left, self.crop_top,
                self.crop_right, self.crop_bottom
            )
        return "For an image of %dx%d resizing to %sx%s, %sit should resize to %sx%s" % (
            self.source_width, self.source_height,
            self.target_width, self.target_height,
            crop_message,
            self.target_width, self.target_height
        )

    def to_context(self):
        self.engine = MockEngine((self.source_width, self.source_height))

        flip_horizontally = self.target_width < 0
        flip_vertically = self.target_height < 0
        self.target_width = self.target_width == "orig" and "orig" or abs(self.target_width)
        self.target_height = self.target_height == "orig" and "orig" or abs(self.target_height)

        importer = Importer(None)
        ctx = Context(server=None, config=None, importer=importer)
        ctx.modules.engine = self.engine

        ctx.request = RequestParameters(
            buffer=None,
            debug=False,
            meta=False,
            crop = {
                'left': self.crop_left,
                'top': self.crop_top,
                'right': self.crop_right,
                'bottom': self.crop_bottom
            },
            adaptive=self.adaptive,
            fit_in=self.fit_in,
            horizontal_flip=flip_horizontally,
            vertical_flip=flip_vertically,
            width=self.target_width,
            height=self.target_height,
            halign=self.halign,
            valign=self.valign,
            focal_points=self.focal_points,
            smart=True,
            extension="JPEG",
            filters=[],
            quality=80,
            image="some.jpeg"
        )

        return ctx

    @property
    def resize_error_message(self):
        message = "The engine resize should have been called with %sx%s" % (self.target_width, self.target_height)
        if not self.engine.calls['resize']:
            return "%s, but was never called" % message
        else:
            last_resize = self.engine.calls['resize'][0]
            return "%s, but was called with %sx%s" % (message, last_resize['width'], last_resize['height'])

    def has_resized_properly(self):
        if not self.target_width and not self.target_height:
            return True

        if (self.target_width == self.source_width and self.target_height == self.source_height) or \
           (self.target_width == self.source_width and self.target_height == "orig") or \
           (self.target_width == "orig" and self.target_height == self.source_height) or \
           (self.target_width == "orig" and self.target_height == "orig"):
            return True

        assert self.engine.calls['resize'], self.resize_error_message

        if not self.target_width:
            assert self.engine.calls['resize'][0]['width'] == float(self.source_width) * self.target_height / self.source_height, self.resize_error_message
            assert self.engine.calls['resize'][0]['height'] == self.target_height, self.resize_error_message
            return True

        if not self.target_height:
            assert self.engine.calls['resize'][0]['width'] == self.target_width, self.resize_error_message
            assert self.engine.calls['resize'][0]['height'] == float(self.source_height) * self.target_width / self.source_width, self.resize_error_message
            return True

        assert self.engine.calls['resize'][0]['width'] == \
            (self.target_width == "orig" and self.source_width or self.target_width), self.resize_error_message
        assert self.engine.calls['resize'][0]['height'] == \
            (self.target_height == "orig" and self.source_height or self.target_height), self.resize_error_message
        return True

    @property
    def crop_error_message(self):
        message = "The engine crop should have been called with %dx%d %dx%d" % (self.crop_left, self.crop_top, self.crop_right, self.crop_bottom)
        if not self.engine.calls['crop']:
            return "%s, but was never called" % message
        else:
            last_crop = self.engine.calls['crop'][0]
            return "%s, but was called with %dx%d %dx%d" % (message, last_crop['left'], last_crop['top'], last_crop['right'], last_crop['bottom'])

    def has_cropped_properly(self):
        if self.crop_left is None:
            assert not self.engine.calls['crop'], 'The engine crop should NOT have been called but was with %(left)dx%(top)d %(right)dx%(bottom)d' % (self.engine.calls['crop'][0])
            return True
        assert self.engine.calls['crop'], self.crop_error_message
        assert self.engine.calls['crop'][0]['left'] == self.crop_left, self.crop_error_message

        assert self.engine.calls['crop'][0]['top'] == self.crop_top, self.crop_error_message

        assert self.engine.calls['crop'][0]['right'] == self.crop_right, self.crop_error_message

        assert self.engine.calls['crop'][0]['bottom'] == self.crop_bottom, self.crop_error_message

        return True

TESTITEMS = [
    TestData(
        source_width=800, source_height=600,
        target_width=400, target_height=150,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=0, crop_top=75, crop_right=800, crop_bottom=375
    ),
    TestData(
        source_width=600, source_height=800,
        target_width=150, target_height=400,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=150, crop_top=0, crop_right=450, crop_bottom=800
    ),
    TestData(
        source_width=600, source_height=800,
        target_width=300, target_height=400,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=800, source_height=600,
        target_width=0, target_height=0,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=800, source_height=600,
        target_width=400, target_height=0,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=200, source_height=140,
        target_width=180, target_height=100,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=0, crop_top=3, crop_right=200, crop_bottom=114
    ),

    # tests with focal points
    TestData(
        source_width=200, source_height=200,
        target_width=100, target_height=100,
        halign="center", valign="middle",
        focal_points=[fp(100, 100, 1)],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=400, source_height=200,
        target_width=100, target_height=100,
        halign="center", valign="middle",
        focal_points=[fp(100, 100, 1)],
        crop_left=50.0, crop_top=0, crop_right=250.0, crop_bottom=200
    ),
    TestData(
        source_width=400, source_height=200,
        target_width=100, target_height=200,
        halign="center", valign="middle",
        focal_points=[fp(100, 50, 1), fp(300, 50, 1)],
        crop_left=150.0, crop_top=0, crop_right=250.0, crop_bottom=200
    ),
    TestData(
        source_width=400, source_height=200,
        target_width=100, target_height=200,
        halign="center", valign="middle",
        focal_points=[fp(100, 150, 1), fp(300, 150, 1)],
        crop_left=150.0, crop_top=0, crop_right=250.0, crop_bottom=200
    ),
    TestData(
        source_width=400, source_height=200,
        target_width=100, target_height=200,
        halign="center", valign="middle",
        focal_points=[fp(100, 50, 1), fp(100, 150, 1)],
        crop_left=75.0, crop_top=0, crop_right=175.0, crop_bottom=200
    ),
    TestData(
        source_width=400, source_height=200,
        target_width=100, target_height=200,
        halign="center", valign="middle",
        focal_points=[fp(300, 50, 1), fp(300, 150, 1)],
        crop_left=225.0, crop_top=0, crop_right=325.0, crop_bottom=200
    ),
    TestData(
        source_width=200, source_height=400,
        target_width=100, target_height=200,
        halign="center", valign="middle",
        focal_points=[fp(100, 50, 1), fp(300, 50, 1)],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=200, source_height=400,
        target_width=100, target_height=200,
        halign="center", valign="middle",
        focal_points=[fp(100, 150, 1), fp(300, 150, 1)],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=200, source_height=400,
        target_width=100, target_height=200,
        halign="center", valign="middle",
        focal_points=[fp(100, 50, 1), fp(100, 150, 1)],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=200, source_height=400,
        target_width=100, target_height=200,
        halign="center", valign="middle",
        focal_points=[fp(300, 50, 1), fp(300, 150, 1)],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=400, source_height=200,
        target_width=100, target_height=100,
        halign="center", valign="middle",
        focal_points=[fp(50, 100, 1), fp(50, 300, 1), fp(150, 100, 1), fp(150, 300, 1)],
        crop_left=50.0, crop_top=0, crop_right=250.0, crop_bottom=200
    ),

    #Width maior

    TestData(
        source_width=800, source_height=600,
        target_width=400, target_height=300,
        halign="center", valign="bottom",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=700, source_height=300,
        target_width=150, target_height=300,
        halign="center", valign="bottom",
        focal_points=[],
        crop_left=275, crop_top=0, crop_right=425, crop_bottom=300
    ),

    TestData(
        source_width=700, source_height=300,
        target_width=300, target_height=150,
        halign="right", valign="bottom",
        focal_points=[],
        crop_left=100, crop_top=0, crop_right=700, crop_bottom=300
    ),

    TestData(
        source_width=700, source_height=300,
        target_width=300, target_height=150,
        halign="left", valign="bottom",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=600, crop_bottom=300
    ),

    TestData(
        source_width=700, source_height=300,
        target_width=150, target_height=300,
        halign="center", valign="bottom",
        focal_points=[],
        crop_left=275, crop_top=0, crop_right=425, crop_bottom=300
    ),

    TestData(
        source_width=700, source_height=300,
        target_width=150, target_height=300,
        halign="left", valign="bottom",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=150, crop_bottom=300
    ),

    TestData(
        source_width=700, source_height=300,
        target_width=150, target_height=300,
        halign="right", valign="bottom",
        focal_points=[],
        crop_left=550, crop_top=0, crop_right=700, crop_bottom=300
    ),

    ##/* Height maior */
    TestData(
        source_width=300, source_height=800,
        target_width=200, target_height=300,
        halign="center", valign="bottom",
        focal_points=[],
        crop_left=0, crop_top=251, crop_right=300, crop_bottom=701
    ),

    TestData(
        source_width=300, source_height=800,
        target_width=200, target_height=300,
        halign="left", valign="bottom",
        focal_points=[],
        crop_left=0, crop_top=251, crop_right=300, crop_bottom=701
    ),

    TestData(
        source_width=300, source_height=800,
        target_width=200, target_height=300,
        halign="right", valign="bottom",
        focal_points=[],
        crop_left=0, crop_top=251, crop_right=300, crop_bottom=701
    ),

    TestData(
        source_width=500, source_height=600,
        target_width=300, target_height=250,
        halign="center", valign="bottom",
        focal_points=[],
        crop_left=0, crop_top=119, crop_right=500, crop_bottom=536
    ),

    TestData(
        source_width=500, source_height=600,
        target_width=300, target_height=250,
        halign="left", valign="bottom",
        focal_points=[],
        crop_left=0, crop_top=119, crop_right=500, crop_bottom=536
    ),

    TestData(
        source_width=500, source_height=600,
        target_width=300, target_height=250,
        halign="right", valign="bottom",
        focal_points=[],
        crop_left=0, crop_top=119, crop_right=500, crop_bottom=536
    ),

    ##Height na proporçao#
    TestData(
        source_width=600, source_height=800,
        target_width=300, target_height=0,
        halign="right", valign="bottom",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=600, source_height=800,
        target_width=300, target_height=0,
        halign="center", valign="bottom",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=600, source_height=800,
        target_width=300, target_height=0,
        halign="left", valign="bottom",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=600, source_height=800,
        target_width=250, target_height=0,
        halign="left", valign="bottom",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=600, source_height=800,
        target_width=250, target_height=0,
        halign="right", valign="bottom",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=600, source_height=800,
        target_width=250, target_height=0,
        halign="center", valign="bottom",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    #Width na proporçao
    TestData(
        source_width=600, source_height=800,
        target_width=0, target_height=400,
        halign="right", valign="bottom",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=600, source_height=800,
        target_width=0, target_height=400,
        halign="left", valign="bottom",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=600, source_height=800,
        target_width=0, target_height=400,
        halign="center", valign="bottom",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=600, source_height=800,
        target_width=0, target_height=350,
        halign="center", valign="bottom",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=600, source_height=800,
        target_width=0, target_height=350,
        halign="left", valign="bottom",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=600, source_height=800,
        target_width=0, target_height=350,
        halign="right", valign="bottom",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=800, source_height=600,
        target_width=400, target_height=150,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=0, crop_top=75, crop_right=800, crop_bottom=375
    ),

    TestData(
        source_width=800, source_height=300,
        target_width=400, target_height=150,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=800, source_height=300,
        target_width=400, target_height=150,
        halign="right", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=800, source_height=300,
        target_width=400, target_height=150,
        halign="left", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=700, source_height=300,
        target_width=300, target_height=150,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=50, crop_top=0, crop_right=650, crop_bottom=300
    ),

    TestData(
        source_width=700, source_height=300,
        target_width=300, target_height=150,
        halign="left", valign="middle",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=600, crop_bottom=300
    ),

    TestData(
        source_width=700, source_height=300,
        target_width=300, target_height=150,
        halign="right", valign="middle",
        focal_points=[],
        crop_left=100, crop_top=0, crop_right=700, crop_bottom=300
    ),

    TestData(
        source_width=700, source_height=300,
        target_width=150, target_height=300,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=275, crop_top=0, crop_right=425, crop_bottom=300
    ),

    TestData(
        source_width=700, source_height=300,
        target_width=150, target_height=300,
        halign="left", valign="middle",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=150, crop_bottom=300
    ),

    TestData(
        source_width=700, source_height=300,
        target_width=150, target_height=300,
        halign="right", valign="middle",
        focal_points=[],
        crop_left=550, crop_top=0, crop_right=700, crop_bottom=300
    ),

    TestData(
        source_width=350, source_height=700,
        target_width=200, target_height=600,
        halign="left", valign="middle",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=234, crop_bottom=700
    ),

    TestData(
        source_width=350, source_height=700,
        target_width=200, target_height=600,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=58, crop_top=0, crop_right=292, crop_bottom=700
    ),

    TestData(
        source_width=350, source_height=700,
        target_width=200, target_height=600,
        halign="right", valign="middle",
        focal_points=[],
        crop_left=116, crop_top=0, crop_right=350, crop_bottom=700
    ),

    TestData(
        source_width=500, source_height=600,
        target_width=300, target_height=250,
        halign="left", valign="middle",
        focal_points=[],
        crop_left=0, crop_top=27, crop_right=500, crop_bottom=444
    ),

    TestData(
        source_width=500, source_height=600,
        target_width=300, target_height=250,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=0, crop_top=27, crop_right=500, crop_bottom=444
    ),

    TestData(
        source_width=500, source_height=600,
        target_width=300, target_height=250,
        halign="right", valign="middle",
        focal_points=[],
        crop_left=0, crop_top=27, crop_right=500, crop_bottom=444
    ),

    TestData(
        source_width=1, source_height=1,
        target_width=0, target_height=0,
        halign="left", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=1, source_height=1,
        target_width=0, target_height=0,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=1, source_height=1,
        target_width=0, target_height=0,
        halign="right", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=200, source_height=400,
        target_width=0, target_height=1,
        halign="left", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=200, source_height=200,
        target_width=16, target_height=16,
        halign="left", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    #--------------------Normal---------------------------------------
    TestData(
        source_width=800, source_height=600,
        target_width=400, target_height=150,
        halign="left", valign="top",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=800, crop_bottom=300
    ),
    TestData(
        source_width=800, source_height=600,
        target_width=400, target_height=150,
        halign="center", valign="top",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=800, crop_bottom=300
    ),
    TestData(
        source_width=800, source_height=600,
        target_width=400, target_height=150,
        halign="right", valign="top",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=800, crop_bottom=300
    ),
    #---------------Normal Invertido---------------------------
    TestData(
        source_width=600, source_height=800,
        target_width=150, target_height=400,
        halign="left", valign="top",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=300, crop_bottom=800
    ),
    TestData(
        source_width=600, source_height=800,
        target_width=150, target_height=400,
        halign="center", valign="top",
        focal_points=[],
        crop_left=150, crop_top=0, crop_right=450, crop_bottom=800
    ),
    TestData(
        source_width=600, source_height=800,
        target_width=150, target_height=400,
        halign="right", valign="top",
        focal_points=[],
        crop_left=300, crop_top=0, crop_right=600, crop_bottom=800
    ),
    #-----------Largo e Baixo---------------------
    TestData(
        source_width=800, source_height=60,
        target_width=400, target_height=15,
        halign="left", valign="top",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=800, crop_bottom=30
    ),
    TestData(
        source_width=800, source_height=60,
        target_width=400, target_height=15,
        halign="center", valign="top",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=800, crop_bottom=30
    ),
    TestData(
        source_width=800, source_height=60,
        target_width=400, target_height=15,
        halign="right", valign="top",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=800, crop_bottom=30
    ),
    #----------------Alto e Estreito--------------------------
    TestData(
        source_width=60, source_height=800,
        target_width=15, target_height=400,
        halign="left", valign="top",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=30, crop_bottom=800
    ),
    TestData(
        source_width=60, source_height=800,
        target_width=15, target_height=400,
        halign="center", valign="top",
        focal_points=[],
        crop_left=15, crop_top=0, crop_right=45, crop_bottom=800
    ),
    TestData(
        source_width=60, source_height=800,
        target_width=15, target_height=400,
        halign="right", valign="top",
        focal_points=[],
        crop_left=30, crop_top=0, crop_right=60, crop_bottom=800
    ),
    #------------------Valores Pequenos--------------------------
    TestData(
        source_width=8, source_height=6,
        target_width=4, target_height=2,
        halign="left", valign="top",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=8, crop_bottom=4
    ),
    TestData(
        source_width=8, source_height=6,
        target_width=4, target_height=2,
        halign="center", valign="top",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=8, crop_bottom=4
    ),
    TestData(
        source_width=8, source_height=6,
        target_width=4, target_height=2,
        halign="right", valign="top",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=8, crop_bottom=4
    ),
    #----------------Valores Pequeno Invertido-------------
    TestData(
        source_width=6, source_height=8,
        target_width=2, target_height=4,
        halign="left", valign="top",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=4, crop_bottom=8
    ),
    TestData(
        source_width=6, source_height=8,
        target_width=2, target_height=4,
        halign="center", valign="top",
        focal_points=[],
        crop_left=1, crop_top=0, crop_right=5, crop_bottom=8
    ),
    TestData(
        source_width=6, source_height=8,
        target_width=2, target_height=4,
        halign="right", valign="top",
        focal_points=[],
        crop_left=2, crop_top=0, crop_right=6, crop_bottom=8
    ),
    #----------------Valores Proporcionais-------------
    TestData(
        source_width=800, source_height=600,
        target_width=400, target_height=300,
        halign="left", valign="top",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=800, source_height=600,
        target_width=400, target_height=300,
        halign="center", valign="top",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=800, source_height=600,
        target_width=400, target_height=300,
        halign="right", valign="top",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    #----------------Valores Iguais-----------------------
    TestData(
        source_width=800, source_height=600,
        target_width=800, target_height=600,
        halign="left", valign="top",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=800, source_height=600,
        target_width=800, target_height=600,
        halign="center", valign="top",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=800, source_height=600,
        target_width=800, target_height=600,
        halign="right", valign="top",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=800, source_height=400,
        target_width=400, target_height="orig",
        halign="middle", valign="middle",
        focal_points=[],
        crop_left=200, crop_top=0, crop_right=600, crop_bottom=400
    )
]

FIT_IN_CROP_DATA = [
    (TestData(
        source_width=800, source_height=400,
        target_width=400, target_height=100,
        halign="middle", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None,
        fit_in=True
    ), (200, 100, 1)),

    (TestData(
        source_width=1000, source_height=250,
        target_width=500, target_height=200,
        halign="middle", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None,
        fit_in=True
    ), (500, 125, 1)),

    (TestData(
        source_width=200, source_height=250,
        target_width=500, target_height=400,
        halign="middle", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None,
        fit_in=True
    ), (200, 250, 0)),

    (TestData(
        source_width=800, source_height=400,
        target_width=100, target_height=400,
        halign="middle", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None,
        fit_in=True, adaptive=True
    ), (200, 100, 1))

]

