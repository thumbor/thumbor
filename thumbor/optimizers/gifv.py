#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import os
import subprocess

from thumbor.optimizers import BaseOptimizer


class Optimizer(BaseOptimizer):

    def should_run(self, image_extension, buffer):
        return 'gif' in image_extension and 'gifv' in self.context.request.filters

    def optimize(self, buffer, input_file, output_file):
        format, command_params = self.set_format()

        command = [
            self.context.config.FFMPEG_PATH,
            '-y',
            '-f',
            'gif',
            '-i',
            input_file,
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
            '-vf',
            'scale=trunc(iw/2)*2:trunc(ih/2)*2',
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
