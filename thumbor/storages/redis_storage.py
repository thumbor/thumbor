#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import logging
import inspect

from json import loads, dumps
from datetime import datetime, timedelta

from redis import Redis, RedisError

from thumbor.storages import BaseStorage
from thumbor.utils import on_exception
from tornado.concurrent import return_future

logger = logging.getLogger('thumbor')


class Storage(BaseStorage):

    storage = None

    def __init__(self, context, shared_client=True):
        '''Initialize the RedisStorage

        :param thumbor.context.Context shared_client: Current context
        :param boolean shared_client: When set to True a singleton client will
                                      be used.
        '''

        BaseStorage.__init__(self, context)
        self.shared_client = shared_client
        self.storage = self.reconnect_redis()

    def get_storage(self):
        '''Get the storage instance.

        :return Redis: Redis instance
        '''

        if self.storage:
            return self.storage
        self.storage = self.reconnect_redis()

        return self.storage

    def reconnect_redis(self):
        if self.shared_client and Storage.storage:
            return Storage.storage

        storage = Redis(
            port=self.context.config.REDIS_STORAGE_SERVER_PORT,
            host=self.context.config.REDIS_STORAGE_SERVER_HOST,
            db=self.context.config.REDIS_STORAGE_SERVER_DB,
            password=self.context.config.REDIS_STORAGE_SERVER_PASSWORD
        )

        if self.shared_client:
            Storage.storage = storage
        return storage

    def on_redis_error(self, fname, exc_type, exc_value):
        '''Callback executed when there is a redis error.

        :param string fname: Function name that was being called.
        :param type exc_type: Exception type
        :param Exception exc_value: The current exception
        :returns: Default value or raise the current exception
        '''

        if self.shared_client:
            Storage.storage = None
        else:
            self.storage = None

        if self.context.config.REDIS_STORAGE_IGNORE_ERRORS is True:
            logger.error("[REDIS_STORAGE] %s" % exc_value)
            if fname == '_exists':
                return False
            return None
        else:
            raise exc_value

    def __key_for(self, url):
        return 'thumbor-crypto-%s' % url

    def __detector_key_for(self, url):
        return 'thumbor-detector-%s' % url

    @on_exception(on_redis_error, RedisError)
    def put(self, path, bytes):
        storage = self.get_storage()
        storage.set(path, bytes)
        storage.expireat(
            path, datetime.now() + timedelta(
                seconds=self.context.config.STORAGE_EXPIRATION_SECONDS
            )
        )

    @on_exception(on_redis_error, RedisError)
    def put_crypto(self, path):
        if not self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            return

        if not self.context.server.security_key:
            raise RuntimeError(
                "STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be True if no "
                "SECURITY_KEY specified"
            )

        key = self.__key_for(path)
        self.get_storage().set(key, self.context.server.security_key)

    @on_exception(on_redis_error, RedisError)
    def put_detector_data(self, path, data):
        key = self.__detector_key_for(path)
        self.get_storage().set(key, dumps(data))

    @return_future
    def get_crypto(self, path, callback):
        callback(self._get_crypto(path))

    @on_exception(on_redis_error, RedisError)
    def _get_crypto(self, path):
        if not self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            return None

        crypto = self.get_storage().get(self.__key_for(path))

        if not crypto:
            return None
        return crypto

    @return_future
    def get_detector_data(self, path, callback):
        callback(self._get_detector_data(path))

    @on_exception(on_redis_error, RedisError)
    def _get_detector_data(self, path):
        data = self.get_storage().get(self.__detector_key_for(path))

        if not data:
            return None
        return loads(data)

    @return_future
    def exists(self, path, callback):
        callback(self._exists(path))

    @on_exception(on_redis_error, RedisError)
    def _exists(self, path):
        return self.get_storage().exists(path)

    @on_exception(on_redis_error, RedisError)
    def remove(self, path):
        self.get_storage().delete(path)

    @return_future
    def get(self, path, callback):
        @on_exception(self.on_redis_error, RedisError)
        def wrap():
            return self.get_storage().get(path)

        callback(wrap())
