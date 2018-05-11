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
from os.path import exists


class Optimizer(BaseOptimizer):

    def should_run(self, image_extension, buffer):
        if image_extension in ['.jpg', '.jpeg']:
            if not exists(self.context.config.JPEGTRAN_PATH):
                logger.warn(
                    'jpegtran optimizer enabled but binary JPEGTRAN_PATH does not exist')
                return False
            return True
        return False

    def run_optimizer(self, image_extension, buffer):
        if not self.should_run(image_extension, buffer):
            return buffer

        if 'strip_icc' in self.context.request.filters:
            copy_chunks = 'comments'
        else:
            # have to copy everything to preserve icc profile
            copy_chunks = 'all'

        command = [
            self.context.config.JPEGTRAN_PATH,
            '-copy',
            copy_chunks,
            '-optimize',
        ]

        if self.context.config.PROGRESSIVE_JPEG:
            command += [
                '-progressive'
            ]

        # close_fds would have a sane default on Python 3 but with Python 2.7 it is False
        # per default but setting it to True + setting any of stdin, stdout, stderr will
        # make this crash on Windows
        # TODO remove close_fds=True if code was upgraded to Python 3
        jpg_process = Popen(command, stdin=PIPE, stdout=PIPE,
                            stderr=PIPE, close_fds=True)
        output_stdout, output_stderr = jpg_process.communicate(buffer)

        if jpg_process.returncode != 0:
            logger.warn('jpegtran finished with non-zero return code (%d): %s'
                        % (jpg_process.returncode, output_stderr))
            return buffer

        return output_stdout
