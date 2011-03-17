#!/usr/bin/env python
#-*- coding: utf8 -*-

from os.path import join

from tornado.options import options, define


define('FILE_LOADER_ROOT_PATH')


def load(path):
    return open(join(options.FILE_LOADER_ROOT_PATH, path)).read()
