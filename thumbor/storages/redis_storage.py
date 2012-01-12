#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from json import loads, dumps
from datetime import datetime, timedelta

import redis

from thumbor.storages import BaseStorage

class Storage(BaseStorage):

    def __init__(self, context):
        BaseStorage.__init__(self, context)

        self.storage = redis.Redis(port=self.context.config.REDIS_STORAGE_SERVER_PORT,
                                   host=self.context.config.REDIS_STORAGE_SERVER_HOST,
                                   db=self.context.config.REDIS_STORAGE_SERVER_DB)

    def __key_for(self, url):
        return 'thumbor-crypto-%s' % url

    def __detector_key_for(self, url):
        return 'thumbor-detector-%s' % url

    def put(self, path, bytes):
        self.storage.set(path, bytes)
        self.storage.expireat(path, datetime.now() + timedelta(seconds=self.context.config.STORAGE_EXPIRATION_SECONDS))

    def put_crypto(self, path):
        if not self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            return

        if not self.context.server.security_key:
            raise RuntimeError("STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be True if no SECURITY_KEY specified")

        self.storage.set(self.__key_for(path), self.context.request.security_key)

    def put_detector_data(self, path, data):
        self.storage.set(self.__detector_key_for(path), dumps(data))

    def get_crypto(self, path):
        if not self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            return None

        crypto = self.storage.get(self.__key_for(path))

        if not crypto:
            return None
        return crypto

    def get_detector_data(self, path):
        data = self.storage.get(self.__detector_key_for(path))

        if not data:
            return None
        return loads(data)

    def get(self, path):
        return self.storage.get(path)

