#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

class FocalPoint(object):
    ALIGNMENT_PERCENTAGES = {
        'left': 0.0,
        'center': 0.5,
        'right': 1.0,
        'top': 0.0,
        'middle': 0.5,
        'bottom': 1.0
    }

    def to_dict(self):
        return {
            'x': self.x,
            'y': self.y,
            'z': self.weight
        }

    @classmethod
    def from_dict(cls, values):
        return cls(float(values['x']), float(values['y']), float(values['z']))

    def __init__(self, x, y, weight=1.0):
        self.x = x
        self.y = y
        self.weight = weight

    @classmethod
    def from_square(cls, x, y, width, height):
        center_x = x + (width / 2)
        center_y = y + (height / 2)
        return cls(center_x, center_y, width * height)

    @classmethod
    def from_alignment(cls, halign, valign, width, height):
        x = width * cls.ALIGNMENT_PERCENTAGES[halign]
        y = height * cls.ALIGNMENT_PERCENTAGES[valign]

        return cls(x, y, 1.0)
