#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import re
import subprocess
from os.path import exists

import webcolors

from thumbor.optimizers import BaseOptimizer
from thumbor.utils import logger


class Optimizer(BaseOptimizer):
    def should_run(self, image_extension, image_buffer):
        if "gif" in image_extension and "gifv" in self.context.request.filters:
            if not exists(self.context.config.FFMPEG_PATH):
                logger.warning(
                    "gifv optimizer enabled but binary FFMPEG_PATH does not exist"
                )
                return False
            return True
        return False

    def optimize(self, image_buffer, input_file, output_file):
        file_format, command_params = self.set_format()

        bg_color_hex = None
        if "background_color" in self.context.request.filters:
            filters = self.context.request.filters.split(":")
            bg_filter = [
                filter for filter in filters if filter.startswith("background_color")
            ][0]
            bg_color = re.search(r"\((.*?)\)", bg_filter).group(1)
            bg_color_hex = self.normalize_color_to_hex(bg_color)

        command = [
            self.context.config.FFMPEG_PATH,
            "-y",
            "-f",
            "gif",
            "-trans_color",
            "0xff%s" % (bg_color_hex[1:] if bg_color_hex else "ffffff"),
            "-i",
            input_file,
            "-filter_complex",
            "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            "-an",
            "-movflags",
            "faststart",
            "-f",
            file_format,
            "-pix_fmt",
            "yuv420p",
        ]

        command += command_params

        command += [
            "-qmin",
            "10",
            "-qmax",
            "42",
            "-crf",
            "23",
            "-maxrate",
            "500k",
            output_file,
            "-loglevel",
            "error",
        ]

        subprocess.call(command, stdin=subprocess.DEVNULL)

        self.context.request.format = file_format

    def set_format(self):
        if "webm" in self.context.request.filters:
            file_format = "webm"
            command_params = ["-quality", "good", "-cpu-used", "4"]
        else:
            file_format = "mp4"
            command_params = ["-profile:v", "baseline", "-level", "4.0"]
        return file_format, command_params

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
            logger.error("background_color value could not be parsed")
