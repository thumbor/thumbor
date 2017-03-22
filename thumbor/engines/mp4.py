#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2017 tubitv.com yingyu@tubitv.com

from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile
import os

from thumbor.engines import BaseEngine
from thumbor.utils import logger


class FfmpegError(RuntimeError):
    pass


class Engine(BaseEngine):

    def __init__(self, context):
        super(Engine, self).__init__(context)
        self.origial_size = 1, 1
        self.corp = 1, 1, 0, 0
        self.image_size = 1, 1
        self.rotate_degrees = 0
        self.flipped_vertically = False
        self.flipped_horizontally = False
        self.grayscale = False

    @property
    def size(self):
        return self.image_size

    def transcode(self, extension):
        mp4_file = NamedTemporaryFile(suffix='.mp4', delete=False)

        if extension == 'webp':
            output_suffix = '.webp'
        else:
            output_suffix = '.gif'
        result_file = NamedTemporaryFile(suffix=output_suffix, delete=False)

        logger.debug('convert {0} to {1}'.format(mp4_file.name, result_file.name))
        try:
            mp4_file.write(self.buffer)
            mp4_file.close()
            result_file.close()

            video_filters = []
            if self.grayscale:
                video_filters.append('hue=s=0')
            if self.flipped_vertically:
                video_filters.append('vflip')
            if self.flip_horizontally:
                video_filters.append('hflip')
            video_filters.append('rotate={0}'.format(self.rotate_degrees))
            video_filters.append('crop={0}'.format(':'.join(map(str, self.corp))))
            video_filters.append('scale={0}'.format(':'.join(map(str, self.image_size))))

            command = [
                self.context.config.FFMPEG_PATH,
                '-i', mp4_file.name,
                '-vf', ', '.join(video_filters),
                '-y', result_file.name
            ]
            p = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE)
            stdout_data = p.communicate()[0]
            if p.returncode != 0:
                logger.debug(p.communicate()[0])
                raise FfmpegError(
                    'ffmpeg command returned errorlevel {0} for command "{1}"'.format(
                        p.returncode, ' '.join(
                            command +
                            [self.context.request.url]
                        )
                    )
                )
            with open(result_file.name, 'r') as f:
                return f.read()
        finally:
            os.unlink(mp4_file.name)
            os.unlink(result_file.name)

    def is_multiple(self):
        return False

    def can_convert_to_webp(self):
        # TODO consider WEBP_SIDE_LIMIT ?
        return True

    def load(self, buffer, extension):
        self.extension = extension
        self.buffer = buffer
        self.image = ''
        command = [
            self.context.config.FFPROBE_PATH,
            '-show_entries', 'stream=height',
            '-show_entries', 'stream=width',
            '-of', 'default=noprint_wrappers=1',
            '-i', '-',
        ]
        p = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        stdout_data = p.communicate(input=self.buffer)[0]
        if p.returncode != 0:
            raise FfmpegError(
                'ffprobe command returned errorlevel {0} for command "{1}"'.format(
                    p.returncode, ' '.join(
                        command +
                        [self.context.request.url]
                    )
                )
            )

        logger.debug(stdout_data)
        width, height = self.origial_size
        for line in stdout_data.split('\n'):
            kv = line.split('=')
            if len(kv) == 2:
                key, value = kv
                if key == 'width':
                    width = int(value)
                elif key == 'height':
                    height = int(value)

        logger.debug('probe result: width={0}, height={1}'.format(width, height))
        self.origial_size = width, height
        self.corp = width, height, 0, 0
        self.image_size = width, height

    def draw_rectangle(self, x, y, width, height):
        raise NotImplementedError()

    def resize(self, width, height):
        self.image_size = width, height

    def crop(self, left, top, right, bottom):
        old_out_width, old_out_height, old_left, old_top = self.corp
        old_width, old_height = self.image_size

        width = right - left
        height = bottom - top
        self.image_size = width, height

        out_width = width / old_width * old_out_width
        out_height = height / old_height * old_out_height
        new_left = old_left + left / old_width * old_out_width
        new_top = old_top + top / old_height * old_out_height
        self.crop = out_width, out_height, left, top

    def rotate(self, degrees):
        self.rotate_degrees = degrees

    def flip_vertically(self):
        self.flipped_vertically = not self.flipped_vertically

    def flip_horizontally(self):
        self.flipped_horizontally = not self.flipped_horizontally

    def convert_to_grayscale(self):
        self.grayscale = True

    # mp4 have no exif data and thus can't be auto oriented
    def reorientate(self, override_exif=True):
        pass

    def read(self, extension=None, quality=None):
        logger.debug('extension={0}, quality={1}'.format(extension, quality))
        return self.transcode(extension)
