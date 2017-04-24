#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import os
import subprocess
import re
import webcolors

from thumbor.optimizers import BaseOptimizer
from thumbor.utils import logger


class Optimizer(BaseOptimizer):

    def should_run(self, image_extension, buffer):
        return 'gif' in image_extension and 'gifv' in self.context.request.filters

    def optimize(self, buffer, input_file, output_file):
        format, command_params = self.set_format()

        bg_color_hex = None
        if 'background_color' in self.context.request.filters:
            filters = self.context.request.filters.split(':')
            bg_filter = [filter for filter in filters if filter.startswith('background_color')][0]
            bg_color = re.search(r'\((.*?)\)', bg_filter).group(1)
            bg_color_hex = self.normalize_color_to_hex(bg_color)

        command = [
            self.context.config.FFMPEG_PATH,
            '-y',
            '-f',
            'lavfi',
            '-i',
            'color=%s' % (bg_color_hex or 'ffffff'),
            '-f',
            'gif',
            '-i',
            input_file,
            '-filter_complex',
            ('[1]reverse,trim=end_frame=1[t];'
                '[1][t]concat[g];[0][g]scale2ref[bg][gif];'
                '[bg]setsar=1[bg];[bg][gif]overlay=shortest=1,'
                'scale=trunc(iw/2)*2:trunc(ih/2)*2'),
            '-an',
            '-movflags',
            'faststart',
            '-f',
            format,
            '-pix_fmt',
            'yuv420p'
        ]

        command += command_params

        command += [
            '-qmin',
            '10',
            '-qmax',
            '42',
            '-crf',
            '23',
            '-maxrate',
            '500k',
            output_file,
            '-loglevel',
            'error'
        ]

        with open(os.devnull) as null:
            subprocess.call(command, stdin=null)
        self.context.request.format = format

    def set_format(self):
        if 'webm' in self.context.request.filters:
            format = 'webm'
            command_params = [
                '-quality',
                'good',
                '-cpu-used',
                '4'
            ]
        else:
            format = 'mp4'
            command_params = [
                '-profile:v',
                'baseline',
                '-level',
                '4.0'
            ]
        return format, command_params

    def normalize_color_to_hex(self, color_string):
        try:
            return webcolors.normalize_hex("#" + color_string)
        except ValueError:
            pass

        try:
            return webcolors.name_to_hex(color_string)
        except ValueError:
            pass

        try:
            return webcolors.normalize_hex(color_string)
        except ValueError:
            pass

        if color_string:
            logger.error('background_color value could not be parsed')
