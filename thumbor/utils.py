#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import os
import logging
from functools import reduce, wraps


def real_import(name):
    if '.' in name:
        return reduce(getattr, name.split('.')[1:], __import__(name))
    return __import__(name)

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
            except self.exception_class:
                if self.callback:
                    self.callback(self_instance) if self_instance else self.callback()
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


def total_seconds_of(delta):
    return (delta.microseconds + (delta.seconds + delta.days * 24 * 3600) * 10.0**6) / 10**6

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
