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
        return 'j2k' in self.context.request.filters

    def optimize(self, buffer, input_file, output_file):
        command = '%s %s -quality %s j2k:%s' % (
            '/usr/local/bin/convert',
            input_file,
            self.context.config.J2K_QUALITY or '100',
            output_file,
        )
        subprocess.call(command, shell=True)
