#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from . import LoaderResult
from . import file_loader
from . import http_loader
from os.path import join, exists, abspath
from urllib import unquote
from tornado.concurrent import return_future


@return_future
def load(context, path, callback):
    file_path = join(context.config.FILE_LOADER_ROOT_PATH.rstrip('/'), unquote(path).lstrip('/'))
    file_path = abspath(file_path)
    inside_root_path = file_path.startswith(context.config.FILE_LOADER_ROOT_PATH)

    result = LoaderResult()

    if inside_root_path and exists(file_path):
        file_loader.load(context, path, callback)
    elif path.startswith('http'):
        http_loader.load(context, path, callback)
    else:
        result.error = LoaderResult.ERROR_NOT_FOUND
        result.successful = False
        callback(result)
