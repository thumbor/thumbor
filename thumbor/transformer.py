#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import math

from thumbor.point import FocalPoint

class Transformer(object):
    def __init__(self, context):
        self.context = context
        self.engine = self.context['engine']
        self.calculate_target_dimensions()
        self.calculate_focal_points()

    def calculate_target_dimensions(self):
        source_width, source_height = self.engine.size

        if not self.context['width'] and not self.context['height']:
            self.target_width = source_width
            self.target_height = source_height
        else:
            if self.context['width']:
                self.target_width = float(self.context['width'])
            else:
                self.target_width = self.engine.get_proportional_width(self.context['height'])

            if self.context['height']:
                self.target_height = float(self.context['height'])
            else:
                self.target_height = self.engine.get_proportional_height(self.context['width'])

    def calculate_focal_points(self):
        source_width, source_height = self.engine.size

        if self.context['focal_points']:
            self.focal_points = self.context['focal_points']
        else:
            self.focal_points = [
                FocalPoint.from_alignment(self.context['halign'],
                                          self.context['valign'],
                                          source_width,
                                          source_height)
            ]

    def transform(self):
        self.manual_crop()
        self.auto_crop()
        self.resize()
        self.flip()

    def manual_crop(self):
        if self.context['should_crop']:
            limit= lambda dimension, maximum: min(max(dimension, 0), maximum)

            source_width, source_height = self.engine.size

            crop_left = limit(self.context['crop_left'], source_width)
            crop_top = limit(self.context['crop_top'], source_height)
            crop_right = limit(self.context['crop_right'], source_width)
            crop_bottom = limit(self.context['crop_bottom'], source_height)

            if crop_left >= crop_right or crop_top >= crop_bottom:
                return

            self.engine.crop(crop_left, crop_top, crop_right, crop_bottom)

    def auto_crop(self):
        source_width, source_height = self.engine.size

        source_ratio = round(float(source_width) / float(source_height), 2)
        target_ratio = round(self.target_width / self.target_height, 2)

        if source_ratio == target_ratio:
            return

        if self.target_width / source_width > self.target_height / source_height:
            crop_width = source_width
            crop_height = math.ceil(source_width * self.target_height / self.target_width)
        else:
            crop_width = math.ceil(self.target_width * source_height / self.target_height)
            crop_height = source_height

        focal_x, focal_y = self.get_center_of_mass()
        focal_x_percentage = focal_x / source_width
        focal_y_percentage = focal_y / source_height

        crop_width_amount = source_width - crop_width
        crop_left = int(crop_width_amount * focal_x_percentage)
        crop_right = int(source_width - crop_width_amount + crop_left)

        crop_height_amount = source_height - crop_height
        crop_top = int(crop_height_amount * focal_y_percentage)
        crop_bottom = int(source_height - crop_height_amount + crop_top)

        self.engine.crop(crop_left, crop_top, crop_right, crop_bottom)

    def flip(self):
        if self.context['should_flip_horizontal']:
            self.engine.flip_horizontally()
        if self.context['should_flip_vertical']:
            self.engine.flip_vertically()

    def get_center_of_mass(self):
        total_weight = 0.0
        total_x = 0.0
        total_y = 0.0

        for focal_point in self.focal_points:
            total_weight += focal_point.weight
            total_x += focal_point.x * focal_point.weight
            total_y += focal_point.y * focal_point.weight

        return total_x / total_weight, total_y / total_weight

    def resize(self):
        source_width, source_height = self.engine.size
        if self.target_width == source_width and self.target_height == source_height:
            return
        self.engine.resize(self.target_width, self.target_height)

