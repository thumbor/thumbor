# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from datetime import datetime
from os import fstat
from os.path import abspath, commonpath, exists, isfile, join
from urllib.parse import unquote

from thumbor.loaders import LoaderResult


def _inside_root_path(root, path):
    try:
        return commonpath([root, path]) == root
    except ValueError:
        return False


async def load(context, path):
    root = abspath(context.config.FILE_LOADER_ROOT_PATH)

    # Decode percent-encoding BEFORE the security check. Checking the
    # encoded path would allow sequences like %2e%2e to pass the
    # abspath/startswith guard and later be decoded into real traversal
    # segments (e.g. unquote("root/%2e%2e/etc/passwd") -> "root/../etc/passwd").
    file_path = abspath(join(root, unquote(path).lstrip("/")))
    inside_root_path = _inside_root_path(root, file_path)

    result = LoaderResult()

    if not inside_root_path:
        result.error = LoaderResult.ERROR_NOT_FOUND
        result.successful = False
        return result

    # Backwards compatibility: if the decoded path does not exist, try the
    # literal (non-decoded) path. This handles files whose names genuinely
    # contain percent-encoded characters (e.g. "image2%20.jpg"). The literal
    # path is safe because abspath already resolved any real ".." segments
    # and the root-boundary check is repeated below.
    if not exists(file_path):
        literal_path = abspath(join(root, path.lstrip("/")))
        if _inside_root_path(root, literal_path) and exists(literal_path):
            file_path = literal_path

    if exists(file_path) and isfile(file_path):
        with open(file_path, "rb") as source_file:
            stats = fstat(source_file.fileno())

            result.successful = True
            result.buffer = source_file.read()

            result.metadata.update(
                size=stats.st_size,
                updated_at=datetime.utcfromtimestamp(stats.st_mtime),
            )
    else:
        result.error = LoaderResult.ERROR_NOT_FOUND
        result.successful = False

    return result
