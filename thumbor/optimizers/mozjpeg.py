#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import os
import subprocess

from thumbor.optimizers import BaseOptimizer

class Optimizer(BaseOptimizer):

    def should_run(self, image_extension, buffer):
        return 'jpg' in image_extension or 'jpeg' in image_extension

    def optimize(self, buffer, input_file, output_file):
        imagemagick_path = self.context.config.IMAGEMAGICK_PATH
        mozjpeg_path = self.context.config.MOZJPEG_PATH
        command = '%s %s pnm:- | %s %s > %s' % (
            imagemagick_path,
            input_file,
            mozjpeg_path,
            self.context.config.MOZJPEG_QUALITY or '80',
            output_file,
        )
        subprocess.call(command, shell=True)
