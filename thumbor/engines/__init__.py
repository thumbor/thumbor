#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

class MultipleEngine:

    def __init__(self, source_engine):
        self.frame_engines = []
        self.source_engine = source_engine

    def add_frame(self, frame):
        frame_engine = self.source_engine.__class__(self.source_engine.context)
        frame_engine.extension = self.source_engine.extension
        frame_engine.source_width = self.source_engine.source_width
        frame_engine.source_height = self.source_engine.source_height
        frame_engine.image = frame

        self.frame_engines.append(frame_engine)

    def read(self, extension=None, quality=None):
        return self.source_engine.read_multiple([frame_engine.image for frame_engine in self.frame_engines], extension)

    def do_many(self, name):
        def exec_func(*args, **kwargs):
            result = []
            for frame_engine in self.frame_engines:
                result.append(getattr(frame_engine, name)(*args, **kwargs))
            return result
        return exec_func

    def __getattr__(self, name):
        if not name in self.__dict__:
            return self.do_many(name)
        return object.__getattr__(self, name)

class BaseEngine(object):

    def __init__(self, context):
        self.context = context
        self.image = None
        self.extension = None
        self.source_width = None
        self.source_height = None
        self.icc_profile = None

    def wrap(self, multiple_engine):
        for method_name in ['resize', 'crop', 'read', 'flip_vertically', 'flip_horizontally']:
            setattr(self, method_name, getattr(multiple_engine, method_name))

    def is_multiple(self):
        return hasattr(self, 'multiple_engine') and self.multiple_engine is not None

    def frame_engines(self):
        return self.multiple_engine.frame_engines

    def load(self, buffer, extension):
        #magic number detection
        if ( buffer[:4] == 'GIF8'):
            extension = '.gif'
        elif ( buffer[:8] == '\x89PNG\r\n\x1a\n'):
            extension = '.png'
        elif ( buffer[:2] == '\xff\xd8'):
            extension = '.jpg'

        self.extension = extension
        imageOrFrames = self.create_image(buffer)

        if isinstance(imageOrFrames, (list, tuple)):
            self.image = imageOrFrames[0]
            if len(imageOrFrames) > 1:
                self.multiple_engine = MultipleEngine(self)
                for frame in imageOrFrames:
                    self.multiple_engine.add_frame(frame)
                self.wrap(self.multiple_engine)
        else:
            self.image = imageOrFrames

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

    def enable_alpha(self):
        raise NotImplementedError()

    def strip_icc(self):
        pass
