#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import os
from shutil import move
from json import dumps, loads
from datetime import datetime
from os.path import exists, dirname, join, getmtime, splitext
import hashlib
from uuid import uuid4

import thumbor.storages as storages


class Storage(storages.BaseStorage):

    def put(self, path, bytes):
        file_abspath = self.path_on_filesystem(path)
        temp_abspath = "%s.%s" % (file_abspath, str(uuid4()).replace('-', ''))
        file_dir_abspath = dirname(file_abspath)

        self.ensure_dir(file_dir_abspath)

        with open(temp_abspath, 'w') as _file:
            _file.write(bytes)

        move(temp_abspath, file_abspath)

        return path

    def put_crypto(self, path):
        if not self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            return

        file_abspath = self.path_on_filesystem(path)
        file_dir_abspath = dirname(file_abspath)

        self.ensure_dir(file_dir_abspath)

        if not self.context.server.security_key:
            raise RuntimeError("STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be True if no SECURITY_KEY specified")

        crypto_path = '%s.txt' % splitext(file_abspath)[0]
        temp_abspath = "%s.%s" % (crypto_path, str(uuid4()).replace('-', ''))
        with open(temp_abspath, 'w') as _file:
            _file.write(self.context.server.security_key)

        move(temp_abspath, crypto_path)

        return file_abspath

    def put_detector_data(self, path, data):
        file_abspath = self.path_on_filesystem(path)

        path = '%s.detectors.txt' % splitext(file_abspath)[0]
        temp_abspath = "%s.%s" % (path, str(uuid4()).replace('-', ''))
        with open(temp_abspath, 'w') as _file:
            _file.write(dumps(data))

        move(temp_abspath, path)

        return file_abspath

    def get_crypto(self, path):
        file_abspath = self.path_on_filesystem(path)
        crypto_file = "%s.txt" % (splitext(file_abspath)[0])

        if not exists(crypto_file):
            return None
        return file(crypto_file).read()

    def get(self, path):
        file_abspath = self.path_on_filesystem(path)

        if not exists(file_abspath) or self.__is_expired(file_abspath):
            return None
        return open(file_abspath, 'r').read()

    def get_detector_data(self, path):
        file_abspath = self.path_on_filesystem(path)
        path = '%s.detectors.txt' % splitext(file_abspath)[0]

        if not exists(path) or self.__is_expired(path):
            return None

        return loads(open(path, 'r').read())

    def path_on_filesystem(self, path):
        digest = hashlib.sha1(path.encode('utf-8')).hexdigest()
        return "%s/%s/%s" % (self.context.config.FILE_STORAGE_ROOT_PATH.rstrip('/'), digest[:2], digest[2:])

    def exists(self, path):
        n_path = self.path_on_filesystem(path)
        return os.path.exists(n_path)

    def remove(self, path):
        n_path = self.path_on_filesystem(path)
        return os.remove(n_path)

    def __is_expired(self, path):
        timediff = datetime.now() - datetime.fromtimestamp(getmtime(path))
        return timediff.seconds > self.context.config.STORAGE_EXPIRATION_SECONDS
