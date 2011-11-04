#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import math
import tempfile

from thumbor.point import FocalPoint

class Transformer(object):
    def __init__(self, context):
        self.context = context
        self.engine = self.context['engine']

    def calculate_target_dimensions(self):
        source_width, source_height = self.engine.size
        source_width = float(source_width)
        source_height = float(source_height)

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

        self.engine.focus(self.focal_points)

    def transform(self):
        self.manual_crop()

        self.calculate_target_dimensions()

        self.smart_detect()

        self.calculate_focal_points()

        if self.context['fit_in']:
            self.fit_in_resize()
        else:
            self.auto_crop()
            self.resize()
        self.flip()

    def smart_detect(self):
        if self.context['detectors'] and self.context['smart']:
            storage = self.context['storage']
            engine = self.context['engine']
            storage_key = '%s_%d_%d' % (self.context['image_url'], engine.size[0], engine.size[1])
            if self.context['crop_left']:
                storage_key = storage_key + '_%d_%d_%d_%d' % (self.context['crop_left'],
                                                              self.context['crop_top'],
                                                              self.context['crop_right'],
                                                              self.context['crop_bottom']
                                                             )
            focal_points = storage.get_detector_data(storage_key)
            if focal_points:
                for point in focal_points:
                    self.context['focal_points'].append(FocalPoint.from_dict(point))
            else:
                with tempfile.NamedTemporaryFile(suffix='.jpg') as temp_file:
                    jpg_buffer = engine.read() if self.context['extension'] in ('.jpg', '.jpeg') else engine.read('.jpg')
                    temp_file.write(jpg_buffer)
                    temp_file.seek(0)
                    self.context['file'] = temp_file.name
                    self.context['detectors'][0](index=0, detectors=self.context['detectors']).detect(self.context)

                points = []
                focal_points = self.context['focal_points']

                for point in focal_points:
                    points.append(point.to_dict())

                storage.put_detector_data(storage_key, points)

    def manual_crop(self):
        if self.context['should_crop']:
            limit = lambda dimension, maximum: min(max(dimension, 0), maximum)

            source_width, source_height = self.engine.size

            crop_left = limit(self.context['crop_left'], source_width)
            crop_top = limit(self.context['crop_top'], source_height)
            crop_right = limit(self.context['crop_right'], source_width)
            crop_bottom = limit(self.context['crop_bottom'], source_height)

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

        if self.target_width / source_width > self.target_height / source_height:
            crop_width = source_width
            crop_height = round(source_width * self.target_height / self.target_width, 0)
        else:
            crop_width = round(math.ceil(self.target_width * source_height / self.target_height), 0)
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
