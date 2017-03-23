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
        self.fps = 5
        self.corp_info = 1, 1, 0, 0
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

        if extension == '.webp':
            output_suffix = '.webp'
        else:
            output_suffix = '.gif'

        try:
            mp4_file.write(self.buffer)
            mp4_file.close()

            video_filters = []
            if self.grayscale:
                video_filters.append('hue=s=0')
            if self.flipped_vertically:
                video_filters.append('vflip')
            if self.flipped_horizontally:
                video_filters.append('hflip')
            video_filters.append('rotate={0}'.format(self.rotate_degrees))
            video_filters.append('crop={0}'.format(':'.join(map(str, self.corp_info))))
            # scale must be the last one
            video_filters.append('scale={0}:flags=lanczos'.format(':'.join(map(str, self.image_size))))

            if output_suffix == '.webp':
                try:
                    result_file = NamedTemporaryFile(suffix=output_suffix, delete=False)
                    logger.debug('convert {0} to {1}'.format(mp4_file.name, result_file.name))
                    result_file.close()
                    command = [
                        self.context.config.FFMPEG_PATH,
                        '-i', mp4_file.name,
                        '-vf', ', '.join(video_filters),
                        '-loop', '0',
                        '-y', result_file.name
                    ]
                    ffmpeg_process = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE)
                    ffmpeg_process.communicate()
                    if ffmpeg_process.returncode != 0:
                        raise FfmpegError(
                            'ffmpeg command returned errorlevel {0} for command "{1}"'.format(
                                ffmpeg_process.returncode, ' '.join(
                                    command +
                                    [self.context.request.url]
                                )
                            )
                        )
                    with open(result_file.name, 'r') as f:
                        return f.read()
                finally:
                    os.unlink(result_file.name)
            else:  # to gif
                palette_file = NamedTemporaryFile(suffix='.png', delete=False)
                ffmpeg_gif_file = NamedTemporaryFile(suffix='.gif', delete=False)
                convert_gif_file = NamedTemporaryFile(suffix='.gif', delete=False)
                convert_optimized_gif_file = NamedTemporaryFile(suffix='.gif', delete=False)
                palette_file.close()
                ffmpeg_gif_file.close()
                convert_gif_file.close()
                convert_optimized_gif_file.close()
                try:
                    # using ffmpeg only
                    ffmpeg_palettegen_cmd = [
                        self.context.config.FFMPEG_PATH,
                        '-i', mp4_file.name,
                        '-vf', ', '.join(video_filters) + ',palettegen',
                        '-y', palette_file.name
                    ]
                    ffmpeg_gif_cmd = [
                        self.context.config.FFMPEG_PATH,
                        '-i', mp4_file.name,
                        '-i', palette_file.name,
                        '-lavfi', ', '.join(video_filters) + '[x];[x][1:v]paletteuse',
                        '-y', ffmpeg_gif_file.name
                    ]
                    ffmpeg_palettegen_process = Popen(ffmpeg_palettegen_cmd, stdout=PIPE, stderr=PIPE)
                    ffmpeg_palettegen_process.communicate()
                    ffmpeg_gif_process = Popen(ffmpeg_gif_cmd, stdout=PIPE, stderr=PIPE)
                    ffmpeg_gif_process.communicate()
                    if ffmpeg_palettegen_process.returncode != 0 or ffmpeg_gif_process.returncode != 0:
                        raise FfmpegError(
                            '{0} => {1}\n{2} => {3}\n\n{4}'.format(
                                ffmpeg_palettegen_process.returncode, ' '.join(ffmpeg_palettegen_cmd),
                                ffmpeg_gif_process.returncode, ' '.join(ffmpeg_gif_cmd),
                                self.context.request.url
                            )
                        )
                    # use ffmpeg and convert
                    ffmpeg_cmd = [
                        self.context.config.FFMPEG_PATH,
                        '-i', mp4_file.name,
                        '-vf', ', '.join(video_filters),
                        '-f', 'image2pipe',
                        '-vcodec', 'ppm',
                        '-'
                    ]
                    convert_gif_cmd = [
                        self.context.config.CONVERT_PATH,
                        '-delay', str(int(100 / self.fps)),
                        '-loop', '0',
                        '-', convert_gif_file.name
                    ]
                    convert_optimize_cmd = [
                        self.context.config.CONVERT_PATH,
                        '-layers', 'Optimize',
                        convert_gif_file.name,
                        convert_optimized_gif_file.name
                    ]
                    ffmpeg_process = Popen(ffmpeg_cmd, stdout=PIPE, stderr=PIPE)
                    convert_gif_process = Popen(convert_gif_cmd, stdout=PIPE, stdin=ffmpeg_process.stdout, stderr=PIPE)
                    convert_gif_process.communicate()
                    convert_optimize_process = Popen(convert_optimize_cmd, stdin=PIPE, stderr=PIPE)
                    convert_optimize_process.communicate()
                    if convert_gif_process.returncode != 0 or convert_optimize_process.returncode != 0:
                        raise FfmpegError(
                            '{0} => {1}\n{2} => {3}\n{4} => {5}\n\n{6}'.format(
                                ffmpeg_process.returncode, ' '.join(ffmpeg_cmd),
                                convert_gif_process.returncode, ' '.join(convert_gif_cmd),
                                convert_optimize_process.returncode, ' '.join(convert_optimize_cmd),
                                self.context.request.url
                            )
                        )
                    result_file_name = ffmpeg_gif_file.name
                    if os.stat(result_file_name).st_size > os.stat(convert_gif_file.name).st_size:
                        result_file_name = convert_gif_file.name
                    if os.stat(result_file_name).st_size > os.stat(convert_optimized_gif_file.name).st_size:
                        result_file_name = convert_optimized_gif_file.name
                    with open(result_file_name, 'r') as f:
                        return f.read()
                finally:
                    os.unlink(palette_file.name)
                    os.unlink(ffmpeg_gif_file.name)
                    os.unlink(convert_gif_file.name)
                    os.unlink(convert_optimized_gif_file.name)
        finally:
            os.unlink(mp4_file.name)

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
            '-show_entries', 'stream=r_frame_rate',
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
        fps = self.fps
        for line in stdout_data.split('\n'):
            kv = line.split('=')
            if len(kv) == 2:
                key, value = kv
                if key == 'width':
                    width = int(value)
                elif key == 'height':
                    height = int(value)
                elif key == 'r_frame_rate':
                    a, b = value.split('/')
                    vb = float(b)
                    if vb > 0:
                        fps = float(a) / vb

        logger.debug('probe result: width={0}, height={1}, fps={2}'.format(width, height, fps))
        self.fps = fps
        self.origial_size = width, height
        self.corp_info = width, height, 0, 0
        self.image_size = width, height

    def draw_rectangle(self, x, y, width, height):
        raise NotImplementedError()

    def resize(self, width, height):
        logger.debug('resize {0} {1}'.format(width, height))
        self.image_size = int(width), int(height)

    def crop(self, left, top, right, bottom):
        logger.debug('crop {0} {1} {2} {3}'.format(left, top, right, bottom))
        old_out_width, old_out_height, old_left, old_top = self.corp_info
        old_width, old_height = self.image_size

        width = int(right - left)
        height = int(bottom - top)
        self.image_size = width, height

        out_width = int(1.0 * width / old_width * old_out_width)
        out_height = int(1.0 * height / old_height * old_out_height)
        new_left = int(old_left + 1.0 * left / old_width * old_out_width)
        new_top = int(old_top + 1.0 * top / old_height * old_out_height)
        self.corp_info = out_width, out_height, new_left, new_top

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
        if quality is None:  # if quality is None, it's called in the storage missed
            return self.buffer  # return the original data, the mp4 file
        return self.transcode(extension)
