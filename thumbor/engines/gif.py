#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from io import BytesIO
from PIL import Image
import re
from subprocess import Popen, PIPE
from thumbor.engines.pil import Engine as PILEngine
from thumbor.utils import logger


GIFSICLE_SIZE_REGEX = re.compile(r'(?:logical\sscreen\s(\d+x\d+))')
GIFSICLE_IMAGE_COUNT_REGEX = re.compile(r'(?:(\d+)\simage)')


class GifSicleError(RuntimeError):
    pass


class Engine(PILEngine):
    @property
    def size(self):
        return self.image_size

    def run_gifsicle(self, command):
        p = Popen([self.context.server.gifsicle_path] + command.split(' '), stdout=PIPE, stdin=PIPE, stderr=PIPE)
        stdout_data = p.communicate(input=self.buffer)[0]
        if p.returncode != 0:
            raise GifSicleError(
                'gifsicle command returned errorlevel {0} for command "{1}" (image maybe corrupted?)'.format(
                    p.returncode, ' '.join(
                        [self.context.server.gifsicle_path] +
                        command.split(' ') +
                        [self.context.request.url]
                    )
                )
            )
        return stdout_data

    def is_multiple(self):
        return self.frame_count > 1

    def update_image_info(self):
        self._is_multiple = False

        result = self.run_gifsicle('--info')
        size = GIFSICLE_SIZE_REGEX.search(result)
        self.image_size = size.groups()[0].split('x')
        self.image_size[0], self.image_size[1] = int(self.image_size[0]), int(self.image_size[1])

        count = GIFSICLE_IMAGE_COUNT_REGEX.search(result)
        self.frame_count = int(count.groups()[0])

    def load(self, buffer, extension):
        self.extension = extension
        self.buffer = buffer
        self.image = ''
        self.operations = []
        self.update_image_info()

    def draw_rectangle(self, x, y, width, height):
        raise NotImplementedError()

    def resize(self, width, height):
        if width == 0 and height == 0:
            return

        if width > 0 and height == 0:
            arguments = "--resize-width %d" % width
        elif height > 0 and width == 0:
            arguments = "--resize-height %d" % height
        else:
            arguments = "--resize %dx%d" % (width, height)

        self.operations.append(arguments)

    def crop(self, left, top, right, bottom):
        arguments = "--crop %d,%d-%d,%d" % (left, top, right, bottom)
        self.operations.append(arguments)
        self.flush_operations()
        self.update_image_info()

    def rotate(self, degrees):
        if degrees not in [90, 180, 270]:
            return
        arguments = '--rotate-%d' % degrees
        self.operations.append(arguments)

    def flip_vertically(self):
        self.operations.append('--flip-vertical')

    def flip_horizontally(self):
        self.operations.append('--flip-horizontal')

    def extract_cover(self):
        arguments = '#0'
        self.operations.append(arguments)
        self.flush_operations()
        self.update_image_info()

    def flush_operations(self):
        if not self.operations:
            return

        self.buffer = self.run_gifsicle(" ".join(self.operations))

        self.operations = []

    def read(self, extension=None, quality=None):
        self.flush_operations()

        # Make sure gifsicle produced a valid gif.
        try:
            with BytesIO(self.buffer) as buff:
                Image.open(buff).verify()
        except Exception:
            self.context.metrics.incr('gif_engine.no_output')
            logger.error("[GIF_ENGINE] invalid gif engine result for url `{url}`.".format(
                url=self.context.request.url
            ))
            raise

        return self.buffer

    def convert_to_grayscale(self):
        self.operations.append('--use-colormap gray')

    # gif have no exif data and thus can't be auto oriented
    def reorientate(self, override_exif=True):
        pass
