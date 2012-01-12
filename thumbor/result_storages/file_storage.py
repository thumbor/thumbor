#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import os
from datetime import datetime

from os.path import exists, dirname, join, getmtime

from thumbor.result_storages import BaseStorage
from thumbor.utils import logger

class Storage(BaseStorage):

    def __ensure_dir(self, path):
        if not exists(path):
            os.makedirs(path)

    def put(self, bytes):
        file_abspath = self.__normalize_path(self.context.request.url)
        file_dir_abspath = dirname(file_abspath)
        logger.debug("[RESULT_STORAGE] putting at %s (%s)" % (file_abspath, file_dir_abspath))

        self.__ensure_dir(file_dir_abspath)

        with open(file_abspath, 'w') as _file:
            _file.write(bytes)

    def get(self):
        path = self.context.request.url
        file_abspath = self.__normalize_path(path)
        logger.debug("[RESULT_STORAGE] getting from %s" % file_abspath)

        if not exists(file_abspath) or self.__is_expired(file_abspath):
            logger.debug("[RESULT_STORAGE] image not found at %s" % file_abspath)
            return None
        return open(file_abspath, 'r').read()

    def __normalize_path(self, path):
        path = join(self.context.config.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH.rstrip('/'), path.lstrip('/'))
        path = path.replace('http://', '')
        return path

    def __is_expired(self, path):
        timediff = datetime.now() - datetime.fromtimestamp(getmtime(path))
        return timediff.seconds > self.context.config.RESULT_STORAGE_EXPIRATION_SECONDS
