#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import os
import subprocess

from thumbor.optimizers import BaseOptimizer
from thumbor.utils import logger

class Optimizer(BaseOptimizer):

    is_media_aware = True

    def should_run(self, media):
        extension = media.file_extension
        logger.debug('gifv extension %s' % extension)

        return 'gif' in extension and 'gifv' in self.context.request.filters

    def optimize(self, media, input_file, output_file):
        format, command_params = self.set_format()
        ffmpeg_path = self.context.config.FFMPEG_PATH
        command = '%s -y -f gif -i %s  -an -movflags faststart -f %s -pix_fmt yuv420p %s -qmin 10 -qmax 42 -crf 23' \
            ' -maxrate 500k -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" %s -loglevel error'

        command = command % (
            ffmpeg_path,
            input_file,
            format,
            command_params,
            output_file,
        )

        with open(os.devnull) as null:
            subprocess.call(command, shell=True, stdin=null)

        self.context.request.format = format

    def set_format(self):
        if 'webm' in self.context.request.filters:
            format = 'webm'
            command_params = '-quality good -cpu-used 4'
        else:
            format = 'mp4'
            command_params = '-profile:v baseline -level 4.0'
        return format, command_params
