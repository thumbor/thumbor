#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from json import loads, dumps
import hashlib

import pylibmc

from thumbor.storages import BaseStorage
from tornado.concurrent import return_future


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

    def get_hash(self, msg):
        msg = msg.encode('utf-8', 'replace')
        return hashlib.sha1(msg).hexdigest()

    def key_for(self, url):
        return self.get_hash(url)

    def crypto_key_for(self, url):
        return self.get_hash('thumbor-crypto-%s' % url)

    def detector_key_for(self, url):
        return self.get_hash('thumbor-detector-%s' % url)

    def put(self, path, contents):
        self.storage.set(self.key_for(path), contents, time=self.context.config.STORAGE_EXPIRATION_SECONDS)
        return path

    def put_crypto(self, path):
        if not self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            return

        if not self.context.server.security_key:
            raise RuntimeError("STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be True if no SECURITY_KEY specified")

        key = self.crypto_key_for(path)
        self.storage.set(key, self.context.server.security_key)
        return key

    def put_detector_data(self, path, data):
        key = self.detector_key_for(path)
        self.storage.set(key, dumps(data))
        return key

    @return_future
    def get_crypto(self, path, callback):
        if not self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            callback(None)
            return

        crypto = self.storage.get(self.crypto_key_for(path))

        callback(crypto if crypto else None)

    @return_future
    def get_detector_data(self, path, callback):
        data = self.storage.get(self.detector_key_for(path))

        callback(loads(data) if data else None)

    @return_future
    def exists(self, path, callback):
        callback(self.storage.get(self.key_for(path)) is not None)

    def remove(self, path):
        if not self.exists(path).result():
            return
        return self.storage.delete(self.key_for(path))

    @return_future
    def get(self, path, callback):
        callback(self.storage.get(self.key_for(path)))
