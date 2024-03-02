#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from datetime import datetime
from os.path import abspath, join
from urllib.parse import unquote

import aiofiles.os

from thumbor.loaders import LoaderResult


async def load(context, path):
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
        return result

    try:
        # keep backwards compatibility, try the actual path first
        # if not found, and not unquote == file_path, try again unquoted path
        result = await file_open(file_path, result)
    except IsADirectoryError:
        result.error = LoaderResult.ERROR_NOT_FOUND
        result.successful = False
    except FileNotFoundError:
        unquoted_file_path = unquote(file_path)
        if file_path != unquoted_file_path:
            try:
                result = await file_open(unquoted_file_path, result)
            except (FileNotFoundError, IsADirectoryError):
                result.error = LoaderResult.ERROR_NOT_FOUND
                result.successful = False
        else:
            result.error = LoaderResult.ERROR_NOT_FOUND
            result.successful = False

    return result


async def file_open(file_path, result):
    async with aiofiles.open(file_path, mode="rb") as a_file:
        # TODO: fstat
        stats = await aiofiles.os.stat(a_file.fileno())
        result.buffer = await a_file.read()
        result.successful = True

        result.metadata.update(
            size=stats.st_size,
            updated_at=datetime.utcfromtimestamp(stats.st_mtime),
        )

    return result
