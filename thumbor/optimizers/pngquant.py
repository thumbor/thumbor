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
        return 'png' in image_extension

    def optimize(self, buffer, input_file, output_file):
        pngquant_path = self.context.config.PNGQUANT_PATH
        # cat %s  | %s --speed=1 --nofs --quality=%s - > %s
        command = 'cat %s  | %s --speed=1 --quality=%s - > %s' % (
            input_file,
            pngquant_path,
            self.context.config.PNGQUANT_QUALITY or '80',
            output_file,
        )
        print(command)
        subprocess.call(command, shell=True)
