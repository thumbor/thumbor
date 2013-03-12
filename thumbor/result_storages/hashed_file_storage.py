#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import os
from datetime import datetime
from uuid import uuid4
from shutil import move
import hashlib

from os.path import exists, dirname, join, getmtime

from thumbor.result_storages import BaseStorage
from thumbor.utils import logger

class Storage(BaseStorage):

    def __ensure_dir(self, path):
        if not exists(path):
            os.makedirs(path)

    def put(self, bytes):
        file_abspath = self.normalize_path(self.context.request.url)
        temp_abspath = "%s.%s" % (file_abspath, str(uuid4()).replace('-',''))
        file_dir_abspath = dirname(file_abspath)
        logger.debug("[RESULT_STORAGE] putting at %s (%s)" % (file_abspath, file_dir_abspath))

        self.__ensure_dir(file_dir_abspath)

        with open(temp_abspath, 'w') as _file:
            _file.write(bytes)

        move(temp_abspath, file_abspath)

    def get(self):
        path = self.context.request.url
        file_abspath = self.normalize_path(path)
        logger.debug("[RESULT_STORAGE] getting from %s" % file_abspath)

        if not exists(file_abspath) or self.is_expired(file_abspath):
            logger.debug("[RESULT_STORAGE] image not found at %s" % file_abspath)
            return None
        with open(file_abspath, 'r') as f:
            return f.read()

    def normalize_path(self, path):
        path = path.replace('http://', '')
        path = path.lstrip('/')
        digest = hashlib.sha1(path.encode('utf-8')).hexdigest()
        path = join(self.context.config.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH.rstrip('/'), digest)
        return path

    def is_expired(self, path):
        expire_in_seconds = self.context.config.get('RESULT_STORAGE_EXPIRATION_SECONDS', None)

        if expire_in_seconds is None or expire_in_seconds == 0:
            return False

        timediff = datetime.now() - datetime.fromtimestamp(getmtime(path))
        return timediff.seconds > expire_in_seconds
