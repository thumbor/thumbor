#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from json import loads, dumps

import pylibmc

from thumbor.storages import BaseStorage


class Storage(BaseStorage):

    def __init__(self, context):
        BaseStorage.__init__(self, context)

        self.storage = pylibmc.Client(
            self.context.config.MEMCACHE_STORAGE_SERVERS,
            binary=True,
            behaviors={
                "tcp_nodelay": True,
                'no_block': True,
                "ketama": True
            }
        )

    def __key_for(self, url):
        return 'thumbor-crypto-%s' % url

    def __detector_key_for(self, url):
        return 'thumbor-detector-%s' % url

    def put(self, path, bytes):
        self.storage.set(
            path,
            bytes,
            time=self.context.config.STORAGE_EXPIRATION_SECONDS
        )

        return path

    def put_crypto(self, path):
        if not self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            return

        if not self.context.server.security_key:
            raise RuntimeError("STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be True if no SECURITY_KEY specified")

        key = self.__key_for(path)
        self.storage.set(key, self.context.server.security_key)
        return key

    def put_detector_data(self, path, data):
        key = self.__detector_key_for(path)
        self.storage.set(key, dumps(data))
        return key

    def get_crypto(self, path, callback):
        if not self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            callback(None)
            return

        crypto = self.storage.get(self.__key_for(path))

        callback(crypto if crypto else None)

    def get_detector_data(self, path, callback):
        data = self.storage.get(self.__detector_key_for(path))

        callback(loads(data) if data else None)

    def exists(self, path):
        return self.storage.get(path) is not None

    def remove(self, path):
        if not self.exists(path):
            return
        return self.storage.delete(path)

    def get(self, path, callback):
        callback(self.storage.get(path))
