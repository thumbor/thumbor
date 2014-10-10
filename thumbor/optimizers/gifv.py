#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import os

from thumbor.optimizers import BaseOptimizer


class Optimizer(BaseOptimizer):

    def should_run(self, image_extension, buffer):
        return 'gif' in image_extension

    def optimize(self, buffer, input_file, output_file):
        ffmpeg_path = self.context.config.FFMPEG_PATH
        if 'gifv()' in self.context.request.filters:
            command = '%s -y -f gif  -i %s  -f mp4 %s' % (
                ffmpeg_path,
                input_file,
                output_file,
            )
            os.system(command)
            self.context.format = 'gifv'
