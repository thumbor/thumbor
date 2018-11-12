#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import hashlib
from os.path import abspath, exists

import tornado.gen

from thumbor.blueprints.loaders import Loader as BaseLoader


def plug_into_lifecycle():
    FileLoader()


class FileLoader(BaseLoader):
    @classmethod
    @tornado.gen.coroutine
    def load_source_image(cls, request, details):
        request_parameters = details.request_parameters

        file_path = "%s/%s" % (
            details.config.FILE_LOADER_ROOT_PATH.rstrip("/"),
            request_parameters.image_url.lstrip("/"),
        )
        file_path = abspath(file_path)
        inside_root_path = file_path.startswith(
            abspath(details.config.FILE_LOADER_ROOT_PATH)
        )

        if inside_root_path and exists(file_path):
            with open(file_path, "rb") as image:
                details.source_image = image.read()

            return

        details.status_code = 502
        details.finish_early = True
        details.headers["Thumbor-File-Loader-Result"] = "Image Not Found"
        details.body = "Could not load source image"
