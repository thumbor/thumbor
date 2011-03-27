#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import os
import tempfile
from datetime import datetime

from tornado.options import options, define
from os.path import exists, dirname, join, getctime

from thumbor.storages import BaseStorage

define('FILE_STORAGE_ROOT_PATH', default=join(tempfile.gettempdir(), 'thumbor', 'storage'))

class Storage(BaseStorage):

    def put(self, path, bytes):
        file_abspath = self.__normalize_path(path)
        file_dir_abspath = dirname(file_abspath)

        if not exists(file_dir_abspath):
            os.makedirs(file_dir_abspath)

        with open(file_abspath, 'w') as _file:
            _file.write(bytes)

    def get(self, path):
        file_abspath = self.__normalize_path(path)
        if not exists(file_abspath) or self.__is_expired(file_abspath):
            return None
        return open(file_abspath, 'r').read()

    def __normalize_path(self, path):
        if path.startswith('/'):
            path = path[1:]

        return join(options.FILE_STORAGE_ROOT_PATH, path)

    def __is_expired(self, path):
        timediff = datetime.now() - datetime.fromtimestamp(getctime(path))
        return timediff.seconds > options.STORAGE_EXPIRATION_SECONDS
