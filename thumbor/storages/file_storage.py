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
from os.path import splitext

from tornado.options import options, define
from os.path import exists, dirname, join, getmtime

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

        if options.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:

            if not options.SECURITY_KEY:
                raise RuntimeError("STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be True if no SECURITY_KEY specified")

            crypto_path = '%s.txt' % splitext(file_abspath)[0]
            with open(crypto_path, 'w') as _file:
                _file.write(options.SECURITY_KEY)

    def get_crypto(self, path):
        file_abspath = self.__normalize_path(path)
        crypto_file = "%s.txt" % (splitext(file_abspath)[0])

        if not exists(crypto_file):
            return None
        return file(crypto_file).read()

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
        timediff = datetime.now() - datetime.fromtimestamp(getmtime(path))
        return timediff.seconds > options.STORAGE_EXPIRATION_SECONDS
