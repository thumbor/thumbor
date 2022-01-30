#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

# pylint: disable=all

from datetime import datetime
from os import fstat
from os.path import abspath, exists, join

from six.moves.urllib.parse import unquote
from tornado.concurrent import return_future

from thumbor.loaders import LoaderResult


@return_future
def load(context, path, callback):
    file_path = join(
        context.config.FILE_LOADER_ROOT_PATH.rstrip("/"), path.lstrip("/")
    )
    file_path = abspath(file_path)
    inside_root_path = file_path.startswith(
        abspath(context.config.FILE_LOADER_ROOT_PATH)
    )

    result = LoaderResult()

    if not inside_root_path:
        result.error = LoaderResult.ERROR_NOT_FOUND
        result.successful = False
        callback(result)
        return

    # keep backwards compatibility, try the actual path first
    # if not found, unquote it and try again
    if not exists(file_path):
        file_path = unquote(file_path)

    if exists(file_path):
        with open(file_path, "rb") as f:
            stats = fstat(f.fileno())

            result.successful = True
            result.buffer = f.read()

            result.metadata.update(
                size=stats.st_size,
                updated_at=datetime.utcfromtimestamp(stats.st_mtime),
            )
    else:
        result.error = LoaderResult.ERROR_NOT_FOUND
        result.successful = False

    callback(result)
