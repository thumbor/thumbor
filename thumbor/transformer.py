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
        self.engine = self.context.modules.engine

    def calculate_target_dimensions(self):
        source_width, source_height = self.engine.size
        source_width = float(source_width)
        source_height = float(source_height)

        if not self.context.request.width and not self.context.request.height:
            self.target_width = source_width
            self.target_height = source_height
        else:
            if self.context.request.width:
                self.target_width = float(self.context.request.width)
            else:
                self.target_width = self.engine.get_proportional_width(self.context.request.height)

            if self.context.request.height:
                self.target_height = float(self.context.request.height)
            else:
                self.target_height = self.engine.get_proportional_height(self.context.request.width)

    def calculate_focal_points(self):
        source_width, source_height = self.engine.size

        if self.context.request.focal_points:
            self.focal_points = self.context.request.focal_points
        else:
            self.focal_points = [
                FocalPoint.from_alignment(self.context.request.halign,
                                          self.context.request.valign,
                                          source_width,
                                          source_height)
            ]

        self.engine.focus(self.focal_points)

    def transform(self, callback):
        self.done_callback = callback
        self.manual_crop()
        self.calculate_target_dimensions()
        self.smart_detect()

    @property
    def smart_storage_key(self):
        key = self.context.request.image_url
        if self.context.request.should_crop:
            key += '_%d_%d_%d_%d' % (self.context.request.crop['left'],
                                     self.context.request.crop['top'],
                                     self.context.request.crop['right'],
                                     self.context.request.crop['bottom'])
        return key

    def smart_detect(self):
        if self.context.modules.detectors and self.context.request.smart:
            storage = self.context.modules.storage
            focal_points = storage.get_detector_data(self.smart_storage_key)
            if focal_points:
                self.after_smart_detect(focal_points)
            else:
                detectors = self.context.modules.detectors
                detectors[0](self.context, index=0, detectors=detectors).detect(self.after_smart_detect)
        else:
            self.after_smart_detect([])

    def after_smart_detect(self, focal_points=[]):
        for point in focal_points:
            self.context.request.focal_points.append(FocalPoint.from_dict(point))

        if self.context.request.focal_points and self.context.modules.storage:
            storage = self.context.modules.storage
            points = []
            for point in self.context.request.focal_points:
                points.append(point.to_dict())

            storage.put_detector_data(self.smart_storage_key, points)

        self.calculate_focal_points()

        if self.context.request.debug:
            self.debug()
        else:
            if self.context.request.fit_in:
                self.fit_in_resize()
            else:
                self.auto_crop()
                self.resize()
            self.flip()

        self.done_callback()

    def manual_crop(self):
        if self.context.request.should_crop:
            limit = lambda dimension, maximum: min(max(dimension, 0), maximum)

            source_width, source_height = self.engine.size

            crop_left = limit(self.context.request.crop['left'], source_width)
            crop_top = limit(self.context.request.crop['top'], source_height)
            crop_right = limit(self.context.request.crop['right'], source_width)
            crop_bottom = limit(self.context.request.crop['bottom'], source_height)

            if crop_left >= crop_right or crop_top >= crop_bottom:
                return

            self.engine.crop(crop_left, crop_top, crop_right, crop_bottom)

            self.calculate_target_dimensions()

    def auto_crop(self):
        source_width, source_height = self.engine.size

        source_ratio = round(float(source_width) / source_height, 2)
        target_ratio = round(float(self.target_width) / self.target_height, 2)

        if source_ratio == target_ratio:
            return

        focal_x, focal_y = self.get_center_of_mass()
        focal_x_percentage = 1.0
        focal_y_percentage = 1.0

        if self.target_width / source_width > self.target_height / source_height:
            crop_width = source_width
            crop_height = round(source_width * self.target_height / self.target_width, 0)
            focal_y_percentage = max(focal_y - (crop_height / 2), 0.0) / source_height
        else:
            crop_width = round(math.ceil(self.target_width * source_height / self.target_height), 0)
            crop_height = source_height
            focal_x_percentage = max(focal_x - (crop_width / 2), 0.0) / source_width

        crop_width_amount = source_width - crop_width
        crop_left = int(crop_width_amount * focal_x_percentage)
        crop_right = int(source_width - crop_width_amount + crop_left)

        crop_height_amount = source_height - crop_height
        crop_top = int(crop_height_amount * focal_y_percentage)
        crop_bottom = int(source_height - crop_height_amount + crop_top)

        self.engine.crop(crop_left, crop_top, crop_right, crop_bottom)

    def flip(self):
        if self.context.request.horizontal_flip:
            self.engine.flip_horizontally()
        if self.context.request.vertical_flip:
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

    def fit_in_resize(self):
        source_width, source_height = self.engine.size

        if self.target_width >= source_width and self.target_height >= source_height:
            return

        if source_width / self.target_width >= source_height / self.target_height:
            resize_height = source_height * self.target_width / source_width
            resize_width = self.target_width
        else:
            resize_height = self.target_height
            resize_width = source_width * self.target_height / source_height

        self.engine.resize(resize_width, resize_height)

    def debug(self):
        if not self.context.request.focal_points:
            return

        for point in self.context.request.focal_points:
            if point.width <= 1:
                point.width = 10
            if point.height <= 1:
                point.height = 10
            self.engine.draw_rectangle(int(point.x - (point.width / 2)),
                                       int(point.y - (point.height / 2)),
                                       point.width,
                                       point.height)

