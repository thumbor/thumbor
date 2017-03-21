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
from tornado import gen


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

    @gen.coroutine
    def get(self, path):
        abs_path = self.path_on_filesystem(path)

        exists = yield self.exists(abs_path, on_filesystem=False)
        if exists:
            with open(self.path_on_filesystem(path), 'r') as f:
                raise gen.Return(f.read())

        raise gen.Return(None)

    @gen.coroutine
    def get_crypto(self, path):
        file_abspath = self.path_on_filesystem(path)
        crypto_file = "%s.txt" % (splitext(file_abspath)[0])

        if exists(crypto_file):
            with open(crypto_file, 'r') as crypto_f:
                raise gen.Return(crypto_f.read())

        raise gen.Return(None)

    @gen.coroutine
    def get_detector_data(self, path):
        file_abspath = self.path_on_filesystem(path)
        path = '%s.detectors.txt' % splitext(file_abspath)[0]

        exists = yield self.exists(path, on_filesystem=False)
        if exists:
            raise gen.Return(loads(open(path, 'r').read()))

        raise gen.Return(None)

    def path_on_filesystem(self, path):
        digest = hashlib.sha1(path.encode('utf-8')).hexdigest()
        return "%s/%s/%s" % (
            self.context.config.FILE_STORAGE_ROOT_PATH.rstrip('/'),
            digest[:2],
            digest[2:]
        )

    @gen.coroutine
    def exists(self, path, on_filesystem=True):
        if on_filesystem:
            path = self.path_on_filesystem(path)

        raise gen.Return(os.path.exists(path) and not self.__is_expired(path))

    def remove(self, path):
        n_path = self.path_on_filesystem(path)
        return os.remove(n_path)

    def __is_expired(self, path):
        if self.context.config.STORAGE_EXPIRATION_SECONDS is None:
            return False
        timediff = datetime.now() - datetime.fromtimestamp(getmtime(path))
        return timediff.seconds > self.context.config.STORAGE_EXPIRATION_SECONDS
