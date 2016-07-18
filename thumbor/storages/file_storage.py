#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import os
from shutil import move
from json import dumps, loads
from datetime import datetime
from os.path import exists, dirname, getmtime, splitext
import hashlib
from uuid import uuid4

import thumbor.storages as storages
from thumbor.utils import logger
from tornado.concurrent import return_future


class Storage(storages.BaseStorage):

    def put(self, path, bytes):
        file_abspath = self.path_on_filesystem(path)
        temp_abspath = "%s.%s" % (file_abspath, str(uuid4()).replace('-', ''))
        file_dir_abspath = dirname(file_abspath)

        logger.debug('creating tempfile for %s in %s...' % (path, temp_abspath))

        self.ensure_dir(file_dir_abspath)

        with open(temp_abspath, 'w') as _file:
            _file.write(bytes)

        logger.debug('moving tempfile %s to %s...' % (temp_abspath, file_abspath))
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
        logger.debug('Stored crypto at %s (security key: %s)' % (crypto_path, self.context.server.security_key))

        return file_abspath

    def put_detector_data(self, path, data):
        file_abspath = self.path_on_filesystem(path)

        path = '%s.detectors.txt' % splitext(file_abspath)[0]
        temp_abspath = "%s.%s" % (path, str(uuid4()).replace('-', ''))

        file_dir_abspath = dirname(file_abspath)
        self.ensure_dir(file_dir_abspath)

        with open(temp_abspath, 'w') as _file:
            _file.write(dumps(data))

        move(temp_abspath, path)

        return file_abspath

    @return_future
    def get(self, path, callback):
        abs_path = self.path_on_filesystem(path)

        def file_exists(resource_available):
            if not resource_available:
                callback(None)
            else:
                with open(self.path_on_filesystem(path), 'r') as f:
                    callback(f.read())

        self.exists(None, file_exists, path_on_filesystem=abs_path)

    @return_future
    def get_crypto(self, path, callback):
        file_abspath = self.path_on_filesystem(path)
        crypto_file = "%s.txt" % (splitext(file_abspath)[0])

        if not exists(crypto_file):
            callback(None)
        else:
            with open(crypto_file, 'r') as crypto_f:
                callback(crypto_f.read())

    @return_future
    def get_detector_data(self, path, callback):
        file_abspath = self.path_on_filesystem(path)
        path = '%s.detectors.txt' % splitext(file_abspath)[0]

        def file_exists(resource_available):
            if not resource_available:
                callback(None)
            else:
                callback(loads(open(path, 'r').read()))
        self.exists(None, file_exists, path_on_filesystem=path)

    def path_on_filesystem(self, path):
        digest = hashlib.sha1(path.encode('utf-8')).hexdigest()
        return "%s/%s/%s" % (
            self.context.config.FILE_STORAGE_ROOT_PATH.rstrip('/'),
            digest[:2],
            digest[2:]
        )

    @return_future
    def exists(self, path, callback, path_on_filesystem=None):
        if path_on_filesystem is None:
            path_on_filesystem = self.path_on_filesystem(path)
        callback(os.path.exists(path_on_filesystem) and not self.__is_expired(path_on_filesystem))

    def remove(self, path):
        n_path = self.path_on_filesystem(path)
        return os.remove(n_path)

    def __is_expired(self, path):
        if self.context.config.STORAGE_EXPIRATION_SECONDS is None:
            return False
        timediff = datetime.now() - datetime.fromtimestamp(getmtime(path))
        return timediff.seconds > self.context.config.STORAGE_EXPIRATION_SECONDS
