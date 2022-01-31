#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import re
from io import BytesIO
from shutil import which
from subprocess import PIPE, Popen

from PIL import Image

from thumbor.engines.pil import Engine as PILEngine
from thumbor.utils import logger

GIFSICLE_SIZE_REGEX = re.compile(r"(?:logical\sscreen\s(\d+x\d+))")
GIFSICLE_IMAGE_COUNT_REGEX = re.compile(r"(?:(\d+)\simage)")


# TODO: Rename this weird error to GifsicleError
class GifSicleError(RuntimeError):
    pass


class Engine(PILEngine):
    @property
    def size(self):
        return self.image_size

    def run_gifsicle(self, command):
        if self.context.server.gifsicle_path is None or not which(
            self.context.server.gifsicle_path
        ):
            raise GifSicleError(
                "gifsicle command was not found and it is required"
                " for your configuration of Thumbor"
            )
        process = Popen(  # pylint: disable=consider-using-with
            [self.context.server.gifsicle_path] + command.split(" "),
            stdout=PIPE,
            stdin=PIPE,
            stderr=PIPE,
        )
        stdout_data, stderr_data = process.communicate(input=self.buffer)
        if process.returncode != 0:
            logger.error(stderr_data)

        if stdout_data is None:
            gifsicle_command = (
                " ".join(
                    [self.context.server.gifsicle_path]
                    + command.split(" ")
                    + [self.context.request.url]
                ),
            )

            raise GifSicleError(
                (
                    f"gifsicle command returned errorlevel {process.returncode} for "
                    f'command "{gifsicle_command}" (image maybe corrupted?)'
                )
            )

        return stdout_data

    def is_multiple(self):
        return self.frame_count > 1

    def update_image_info(self):
        self._is_multiple = False

        result = self.run_gifsicle("--info").decode("utf-8")
        size = GIFSICLE_SIZE_REGEX.search(result)
        self.image_size = size.groups()[0].split("x")
        self.image_size[0], self.image_size[1] = (
            int(self.image_size[0]),
            int(self.image_size[1]),
        )

        count = GIFSICLE_IMAGE_COUNT_REGEX.search(result)
        self.frame_count = int(count.groups()[0])

    def load(self, buffer, extension):
        self.extension = extension
        self.buffer = buffer
        self.image = ""
        self.operations = []
        self.update_image_info()

    def draw_rectangle(self, x, y, width, height):
        raise NotImplementedError()

    def resize(self, width, height):
        if width == 0 and height == 0:
            return

        if width > 0 and height == 0:
            arguments = f"--resize-width {width}"
        elif height > 0 and width == 0:
            arguments = f"--resize-height {height}"
        else:
            arguments = f"--resize {width}x{height}"

        self.operations.append(arguments)

    def crop(self, left, top, right, bottom):
        arguments = f"--crop {left},{top}-{right},{bottom}"
        self.operations.append(arguments)
        self.flush_operations()
        self.update_image_info()

    def rotate(self, degrees):
        if degrees not in [90, 180, 270]:
            return
        arguments = f"--rotate-{degrees}"
        self.operations.append(arguments)

    def flip_vertically(self):
        self.operations.append("--flip-vertical")

    def flip_horizontally(self):
        self.operations.append("--flip-horizontal")

    def extract_cover(self):
        arguments = "#0"
        self.operations.append(arguments)
        self.flush_operations()
        self.update_image_info()

    def flush_operations(self, update_image=True):
        if not self.operations:
            return self.buffer

        buffer = self.run_gifsicle(" ".join(self.operations))

        self.operations = []

        if update_image:
            self.buffer = buffer

        return buffer

    def read(self, extension=None, quality=None):
        return self._read()

    def _read(self, update_image=True):
        buffer = self.flush_operations(update_image)

        # Make sure gifsicle produced a valid gif.
        try:
            with BytesIO(buffer) as buff:
                Image.open(buff).verify()
        except Exception:
            self.context.metrics.incr("gif_engine.no_output")
            logger.error(
                "[GIF_ENGINE] invalid gif engine result for url `%s`.",
                self.context.request.url,
            )
            raise

        return buffer

    def convert_to_grayscale(self, update_image=True, alpha=True):
        self.operations.append("--use-colormap gray")
        return self._read(update_image)

    # gif have no exif data and thus can't be auto oriented
    def reorientate(self, override_exif=True):
        pass
