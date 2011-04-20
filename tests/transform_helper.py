#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

class MockEngine(object):
    def __init__(self, size):
        self.size = size
        self.calls = {
            'resize': [],
            'crop': []
        }

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

    def get_proportional_width(self, new_height):
        width, height = self.size
        return float(new_height) * width / height

    def get_proportional_height(self, new_width):
        width, height = self.size
        return float(new_width) * height / width


class TestData(object):
    def __init__(self, 
            source_width, source_height,
            target_width, target_height,
            halign, valign, focal_points,
            crop_left, crop_top, crop_right, crop_bottom,
            fit_in=False):
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
        return "For an image of %dx%d resizing to %dx%d, %sit should resize to %dx%d" % (
            self.source_width, self.source_height,
            self.target_width, self.target_height,
            crop_message,
            self.target_width, self.target_height
        )

    def to_context(self):
        self.engine = MockEngine((self.source_width, self.source_height))

        context = dict(
            loader=None,
            engine=self.engine,
            storage=None,
            buffer=None,
            should_crop=False,
            crop_left=None,
            crop_top=None,
            crop_right=None,
            crop_bottom=None,
            fit_in=self.fit_in,
            should_flip_horizontal=False,
            width=self.target_width,
            should_flip_vertical=False,
            height=self.target_height,
            halign=self.halign,
            valign=self.valign,
            focal_points=self.focal_points,
            should_be_smart=True,
            extension="JPEG"
        )

        return context

    @property
    def resize_error_message(self):
        message = "The engine resize should have been called with %dx%d" % (self.target_width, self.target_height)
        if not self.engine.calls['resize']:
            return "%s, but was never called" % message
        else:
            last_resize = self.engine.calls['resize'][0]
            return "%s, but was called with %dx%d" % (message, last_resize['width'], last_resize['height'])

    def has_resized_properly(self):
        if not self.target_width and not self.target_height:
            return True

        if self.target_width == self.source_width and self.target_height == self.source_height:
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

        assert self.engine.calls['resize'][0]['width'] == self.target_width, self.resize_error_message
        assert self.engine.calls['resize'][0]['height'] == self.target_height, self.resize_error_message
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
