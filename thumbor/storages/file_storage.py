#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import os
from json import dumps, loads
from datetime import datetime
from os.path import splitext

from os.path import exists, dirname, join, getmtime

from thumbor.storages import BaseStorage

class Storage(BaseStorage):

    def __ensure_dir(self, path):
        if not exists(path):
            os.makedirs(path)

    def put(self, path, bytes):
        file_abspath = self.__normalize_path(path)
        file_dir_abspath = dirname(file_abspath)

        self.__ensure_dir(file_dir_abspath)

        with open(file_abspath, 'w') as _file:
            _file.write(bytes)

    def put_crypto(self, path):
        if not self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            return

        file_abspath = self.__normalize_path(path)
        file_dir_abspath = dirname(file_abspath)

        self.__ensure_dir(file_dir_abspath)

        if not self.context.config.SECURITY_KEY:
            raise RuntimeError("STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be True if no SECURITY_KEY specified")

        crypto_path = '%s.txt' % splitext(file_abspath)[0]
        with open(crypto_path, 'w') as _file:
            _file.write(self.context.config.SECURITY_KEY)

    def put_detector_data(self, path, data):
        file_abspath = self.__normalize_path(path)

        path = '%s.detectors.txt' % splitext(file_abspath)[0]
        with open(path, 'w') as _file:
            _file.write(dumps(data))

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

    def get_detector_data(self, path):
        file_abspath = self.__normalize_path(path)
        path = '%s.detectors.txt' % splitext(file_abspath)[0]

        if not exists(path) or self.__is_expired(path):
            return None

        return loads(open(path, 'r').read())

    def __normalize_path(self, path):
        return join(self.context.config.FILE_STORAGE_ROOT_PATH.rstrip('/'), path.lstrip('/'))

    def __is_expired(self, path):
        timediff = datetime.now() - datetime.fromtimestamp(getmtime(path))
        return timediff.seconds > self.context.config.STORAGE_EXPIRATION_SECONDS
