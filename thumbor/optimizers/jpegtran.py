#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from subprocess import Popen, PIPE

from thumbor.optimizers import BaseOptimizer
from thumbor.utils import logger


class Optimizer(BaseOptimizer):

    def should_run(self, image_extension, buffer):
        return image_extension in ['.jpg', '.jpeg']

    def run_optimizer(self, image_extension, buffer):
        if not self.should_run(image_extension, buffer):
            return buffer

        command = [
            self.context.config.JPEGTRAN_PATH,
            '-copy',
            'comments',
            '-optimize',
        ]

        if self.context.config.PROGRESSIVE_JPEG:
            command += [
                '-progressive'
            ]

        jpg_process = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output_stdout, output_stderr = jpg_process.communicate(buffer)

        if jpg_process.returncode != 0:
            logger.warn('jpegtran finished with non-zero return code (%d): %s'
                        % (jpg_process.returncode, output_stderr))
            return buffer

        return output_stdout
