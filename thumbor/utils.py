#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import os
import logging
from functools import wraps


CONTENT_TYPE = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.png': 'image/png',
    '.webp': 'image/webp',
    '.mp4': 'video/mp4',
    '.webm': 'video/webm',
    '.svg': 'image/svg+xml',
    '.tif': 'image/tiff',
    '.tiff': 'image/tiff'
}

EXTENSION = {
    'image/jpeg': '.jpg',
    'image/gif': '.gif',
    'image/png': '.png',
    'image/webp': '.webp',
    'video/mp4': '.mp4',
    'video/webm': '.webm',
    'image/svg+xml': '.svg',
    'image/tiff': '.tif'
}


logger = logging.getLogger('thumbor')


class on_exception(object):

    def __init__(self, callback, exception_class=Exception):
        self.callback = callback
        self.exception_class = exception_class

    def __call__(self, fn):
        def wrapper(*args, **kwargs):
            self_instance = args[0] if len(args) > 0 else None
            try:
                return fn(*args, **kwargs)
            except self.exception_class as exc_value:
                if self.callback:
                    # Execute the callback and let it handle the exception
                    if self_instance:
                        return self.callback(
                            self_instance,
                            fn.__name__,
                            self.exception_class,
                            exc_value
                        )
                    else:
                        return self.callback(
                            fn.__name__,
                            self.exception_class,
                            exc_value
                        )
                else:
                    raise

        return wrapper


class deprecated(object):

    def __init__(self, msg=None):
        self.msg = ": {0}".format(msg) if msg else "."

    def __call__(self, func):
        @wraps(func)
        def new_func(*args, **kwargs):
            logger.warn(
                "Deprecated function {0}{1}".format(func.__name__, self.msg)
            )
            return func(*args, **kwargs)
        return new_func


def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None
