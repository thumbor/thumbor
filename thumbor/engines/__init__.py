#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

class BaseEngine(object):

    def __init__(self, context):
        self.context = context
        self.image = None
        self.extension = None
        self.source_width = None
        self.source_height = None
        self.icc_profile = None

    def load(self, buffer, extension):
        self.extension = extension
        self.image = self.create_image(buffer)
        if self.source_width is None:
            self.source_width = self.size[0]
        if self.source_height is None:
            self.source_height = self.size[1]

    @property
    def size(self):
        return self.image.size

    def normalize(self):
        width, height = self.size
        self.source_width = width
        self.source_height = height

        if width > self.context.config.MAX_WIDTH or height > self.context.config.MAX_HEIGHT:
            width_diff = width - self.context.config.MAX_WIDTH
            height_diff = height - self.context.config.MAX_HEIGHT
            if self.context.config.MAX_WIDTH and width_diff > height_diff:
                height = self.get_proportional_height(self.context.config.MAX_WIDTH)
                self.resize(self.context.config.MAX_WIDTH, height)
                return True
            elif self.context.config.MAX_HEIGHT and height_diff > width_diff:
                width = self.get_proportional_width(self.context.config.MAX_HEIGHT)
                self.resize(width, self.context.config.MAX_HEIGHT)
                return True

        return False

    def get_proportional_width(self, new_height):
        width, height = self.size
        return round(float(new_height) * width / height, 0)

    def get_proportional_height(self, new_width):
        width, height = self.size
        return round(float(new_width) * height / width, 0)

    def gen_image(self):
        raise NotImplementedError()

    def create_image(self):
        raise NotImplementedError()

    def crop(self):
        raise NotImplementedError()

    def resize(self):
        raise NotImplementedError()

    def focus(self, points):
        pass

    def flip_horizontally(self):
        raise NotImplementedError()
    
    def flip_vertically(self):
        raise NotImplementedError()

    def read(self, extension, quality):
        raise NotImplementedError()

    def get_image_data(self):
        raise NotImplementedError()

    def set_image_data(self, data):
        raise NotImplementedError()

    def get_image_mode(self):
        """ Possible return values should be: RGB, RBG, GRB, GBR, BRG, BGR, RGBA, AGBR, ...  """
        raise NotImplementedError()

    def paste(self):
        raise NotImplementedError()
