#!/usr/bin/env python
#-*- coding: utf8 -*-

from tornado.options import options

class BaseEngine(object):

    def __init__(self):
        self.image = None

    def load(self, buffer):
        #loads image buffer in byte format.
        if not self.image:
            self.image = self.create_image(buffer)

    @property
    def size(self):
        # returns the image size as a tuple
        return self.image.size

    def normalize(self):
        width, height = self.image.size
        if width > options.MAX_WIDTH or height > options.MAX_HEIGHT:
            width_diff = width - options.MAX_WIDTH
            height_diff = height - options.MAX_HEIGHT
            if width_diff > height_diff:
                height = self.get_proportional_height(options.MAX_WIDTH)
                self.resize(options.MAX_WIDTH, height)
            else:
                width = self.get_proportional_width(options.MAX_HEIGHT)
                self.resize(width, options.MAX_HEIGHT)
    
    def get_proportional_width(self, new_height):
        width, height = self.size
        return new_height * width / height
        
    def get_proportional_height(self, new_width):
        width, height = self.size
        return new_width * height / width
        
    def create_image(self):
        raise NotImplementedError()

    