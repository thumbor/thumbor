#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pexif import ExifSegment

from thumbor.utils import logger, EXTENSION

WEBP_SIDE_LIMIT = 16383


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

    def size(self):
        return self.frame_engines[0].size

    def do_many(self, name):
        def exec_func(*args, **kwargs):
            result = []
            for frame_engine in self.frame_engines:
                result.append(getattr(frame_engine, name)(*args, **kwargs))
            return result
        return exec_func


class BaseEngine(object):

    def __init__(self, context):
        self.context = context
        self.image = None
        self.extension = None
        self.source_width = None
        self.source_height = None
        self.icc_profile = None
        self.frame_count = 1

    @classmethod
    def get_mimetype(cls, buffer):
        mime = None

        # magic number detection
        if buffer.startswith('GIF8'):
            mime = 'image/gif'
        elif buffer.startswith('\x89PNG\r\n\x1a\n'):
            mime = 'image/png'
        elif buffer.startswith('\xff\xd8'):
            mime = 'image/jpeg'
        elif buffer.startswith('WEBP', 8):
            mime = 'image/webp'
        elif buffer.startswith('\x00\x00\x00\x0c'):
            mime = 'image/jp2'
        elif buffer.startswith('\x00\x00\x00 ftyp'):
            mime = 'video/mp4'
        elif buffer.startswith('\x1aE\xdf\xa3'):
            mime = 'video/webm'

        return mime

    def wrap(self, multiple_engine):
        for method_name in ['resize', 'crop', 'flip_vertically', 'flip_horizontally']:
            setattr(self, method_name, multiple_engine.do_many(method_name))
        setattr(self, 'read', multiple_engine.read)

    def is_multiple(self):
        return hasattr(self, 'multiple_engine') and self.multiple_engine is not None

    def frame_engines(self):
        return self.multiple_engine.frame_engines

    def load(self, buffer, extension):
        self.extension = extension
        if extension is None:
            mime = self.get_mimetype(buffer)
            self.extension = EXTENSION.get(mime, '.jpg')

        image_or_frames = self.create_image(buffer)

        if self.context.config.ALLOW_ANIMATED_GIFS and isinstance(image_or_frames, (list, tuple)):
            self.image = image_or_frames[0]
            if len(image_or_frames) > 1:
                self.multiple_engine = MultipleEngine(self)
                for frame in image_or_frames:
                    self.multiple_engine.add_frame(frame)
                self.wrap(self.multiple_engine)
        else:
            self.image = image_or_frames

        if self.source_width is None:
            self.source_width = self.size[0]
        if self.source_height is None:
            self.source_height = self.size[1]

    @property
    def size(self):
        if self.is_multiple():
            return self.multiple_engine.size()
        return self.image.size

    def can_convert_to_webp(self):
        return self.size[0] <= WEBP_SIDE_LIMIT and self.size[1] <= WEBP_SIDE_LIMIT

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

    def get_orientation(self, override_exif=True):
        if (not hasattr(self, 'exif')) or self.exif is None:
            return

        orientation = None

        try:
            segment = ExifSegment(None, None, self.exif, 'ro')
            primary = segment.primary
            orientation = primary['Orientation']
            if orientation:
                orientation = orientation[0]
                if orientation != 1 and override_exif:
                    primary['Orientation'] = [1]
                    self.exif = segment.get_data()
        except Exception:
            logger.exception('Ignored error handling exif for reorientation')
        finally:
            return orientation

    def reorientate(self):

        orientation = self.get_orientation()

        if orientation == 2:
            self.flip_horizontally()
        elif orientation == 3:
            self.rotate(180)
        elif orientation == 4:
            self.flip_vertically()
        elif orientation == 5:
            # Horizontal Mirror + Rotation 270
            self.flip_vertically()
            self.rotate(270)
        elif orientation == 6:
            self.rotate(270)
        elif orientation == 7:
            # Vertical Mirror + Rotation 270
            self.flip_horizontally()
            self.rotate(270)
        elif orientation == 8:
            self.rotate(90)

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

    def rotate(self):
        pass

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

    def image_data_as_rgb(self, update_image=True):
        raise NotImplementedError()

    def strip_icc(self):
        pass

    def extract_cover(self):
        raise NotImplementedError()

    def cleanup(self):
        pass
