#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from os.path import exists
from subprocess import PIPE, Popen

from thumbor.optimizers import BaseOptimizer
from thumbor.utils import logger


class Optimizer(BaseOptimizer):
    def should_run(self, image_extension, image_buffer):
        if image_extension in [".jpg", ".jpeg"]:
            if self.context.config.JPEGTRAN_PATH is None or not exists(
                self.context.config.JPEGTRAN_PATH
            ):
                logger.warning(
                    "jpegtran optimizer enabled but binary JPEGTRAN_PATH does not exist"
                )
                return False
            return True
        return False

    def run_optimizer(self, image_extension, buffer):
        if not self.should_run(image_extension, buffer):
            return buffer

        if "strip_icc" in self.context.request.filters:
            copy_chunks = "comments"
        else:
            # have to copy everything to preserve icc profile
            copy_chunks = "all"

        command = [
            self.context.config.JPEGTRAN_PATH,
            "-copy",
            copy_chunks,
            "-optimize",
        ]

        if self.context.config.PROGRESSIVE_JPEG:
            command += ["-progressive"]

        if self.context.config.JPEGTRAN_SCANS_FILE:
            if exists(self.context.config.JPEGTRAN_SCANS_FILE):
                command += ["-scans", self.context.config.JPEGTRAN_SCANS_FILE]
            else:
                logger.warning("jpegtran optimizer scans file does not exist")

        jpg_process = Popen(  # pylint: disable=consider-using-with
            command, stdin=PIPE, stdout=PIPE, stderr=PIPE
        )
        output_stdout, output_stderr = jpg_process.communicate(buffer)

        if jpg_process.returncode != 0:
            logger.warning(
                "jpegtran finished with non-zero return code (%d): %s",
                jpg_process.returncode,
                output_stderr,
            )
            return buffer

        return output_stdout
