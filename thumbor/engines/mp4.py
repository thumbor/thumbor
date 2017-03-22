#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2017 tubitv.com yingyu@tubitv.com

from thumbor.engines import BaseEngine
from subprocess import Popen, PIPE

class FfmpegError(RuntimeError):
    pass

class Engine(BaseEngine):

    def __init__(self, context):
        super(Engine, self).__init__(context)
        self.frame_count = 0
        self.image_size = 0, 0

    @property
    def size(self):
        return self.image_size

    def run_ffmpeg(self):
        # TODO
        command = [self.context.config.FFMPEG_PATH, '-version']
        p = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        stdout_data = p.communicate(input=self.buffer)[0]
        if p.returncode != 0:
            raise FfmpegError(
                'ffmpeg command returned errorlevel {0} for command "{1}"'.format(
                    p.returncode, ' '.join(
                        command +
                        [self.context.request.url]
                    )
                )
            )
        return stdout_data

    def is_multiple(self):
        return self.frame_count > 1

    def update_image_info(self):
        # TODO update frame_count, image_size
        pass

    def load(self, buffer, extension):
        self.extension = extension
        self.buffer = buffer
        self.image = ''
        self.operations = []
        self.update_image_info()

    def draw_rectangle(self, x, y, width, height):
        raise NotImplementedError()

    def resize(self, width, height):
        # TODO add parameter to ffmpeg
        pass

    def crop(self, left, top, right, bottom):
        # TODO add parameter to ffmpeg
        # TODO execute the croping
        # TODO update image info
        pass

    def rotate(self, degrees):
        # TODO add parameter to ffmpeg
        pass

    def flip_vertically(self):
        # TODO add parameter to ffmpeg
        pass

    def flip_horizontally(self):
        # TODO add parameter to ffmpeg
        pass

    def extract_cover(self):
        # TODO add parameter to ffmpeg
        pass

    def flush_operations(self):
        # TODO execute the cached operations
        pass

    def convert_to_grayscale(self):
        # TODO execute the cached operations
        pass

    # gif have no exif data and thus can't be auto oriented
    def reorientate(self, override_exif=True):
        pass

    def read(self, extension=None, quality=None):
        self.flush_operations()
        # TODO verify the buffer is a valid gif/webp
        return self.buffer
