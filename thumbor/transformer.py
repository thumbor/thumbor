#!/usr/bin/python
# -*- coding: utf-8 -*-

import math

from thumbor.point import FocalPoint

class Transformer(object):
    def __init__(self, context, source_width, source_height):
        self.context = context
        self.engine = self.context['engine']
        self.source_width = float(source_width)
        self.source_height = float(source_height)
        self.calculate_target_dimensions()
        self.calculate_focal_points()
        
    def calculate_target_dimensions(self):
        if not self.context['width'] and not self.context['height']:
            self.target_width = self.source_width
            self.target_height = self.source_height
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
        if self.context['focal_points']:
            self.focal_points = self.context['focal_points']
        else:
            self.focal_points = [
                FocalPoint.from_alignment(self.context['halign'],
                                          self.context['valign'],
                                          self.source_width,
                                          self.source_height)
            ]

    def transform(self):
        source_ratio = round(self.source_width / self.source_height, 2)
        target_ratio = round(self.target_width / self.target_height, 2)
        if source_ratio != target_ratio:
            self.crop()
        self.resize()

    def crop(self):
        
        if self.target_width / self.source_width > self.target_height / self.source_height:
            crop_width = self.source_width
            crop_height = math.ceil(self.source_width * self.target_height / self.target_width)
        else:
            crop_width = math.ceil(self.target_width * self.source_height / self.target_height)
            crop_height = self.source_height

        focal_x, focal_y = self.get_center_of_mass()
        focal_x_percentage = focal_x / self.source_width
        focal_y_percentage = focal_y / self.source_height

        crop_width_amount = self.source_width - crop_width
        crop_left = int(crop_width_amount * focal_x_percentage)
        crop_right = int(self.source_width - crop_width_amount + crop_left)

        crop_height_amount = self.source_height - crop_height
        crop_top = int(crop_height_amount * focal_y_percentage)
        crop_bottom = int(self.source_height - crop_height_amount + crop_top)

        self.engine.crop(crop_left, crop_top, crop_right, crop_bottom)

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
        self.engine.resize(self.target_width, self.target_height)

