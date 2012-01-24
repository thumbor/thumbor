#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import redis
from pyvows import Vows, expect

from thumbor.storages.redis_storage import Storage as RedisStorage
from thumbor.context import Context
from thumbor.config import Config
from fixtures.redis_storage_fixture import IMAGE_URL, IMAGE_BYTES, get_server

class RedisDBContext(Vows.Context):
    def setup(self):
        self.connection = redis.Redis(port=7778,
                                      host='localhost',
                                      db=0)

@Vows.batch
class RedisStorageVows(RedisDBContext):
    class CanStoreImage(Vows.Context):
        def topic(self):
            config = Config(REDIS_STORAGE_SERVER_PORT=7778)
            storage = RedisStorage(Context(config=config, server=get_server('ACME-SEC')))
            storage.put(IMAGE_URL % 1, IMAGE_BYTES)
            return self.parent.connection.get(IMAGE_URL % 1)

        def should_be_in_catalog(self, topic):
            expect(topic).not_to_be_null()
            expect(topic).not_to_be_an_error()

    class CanGetImage(Vows.Context):
        def topic(self):
            config = Config(REDIS_STORAGE_SERVER_PORT=7778)
            storage = RedisStorage(Context(config=config, server=get_server('ACME-SEC')))

            storage.put(IMAGE_URL % 2, IMAGE_BYTES)
            return storage.get(IMAGE_URL % 2)

        def should_not_be_null(self, topic):
            expect(topic).not_to_be_null()
            expect(topic).not_to_be_an_error()

        def should_have_proper_bytes(self, topic):
            expect(topic).to_equal(IMAGE_BYTES)

    class CryptoVows(Vows.Context):
        class DoesNotStoreIfConfigSaysNotTo(Vows.Context):
            def topic(self):
                config = Config(REDIS_STORAGE_SERVER_PORT=7778)
                storage = RedisStorage(Context(config=config, server=get_server('ACME-SEC')))
                storage.put(IMAGE_URL % 2, IMAGE_BYTES)
                storage.put_crypto(IMAGE_URL % 2)
                return storage.get_crypto(IMAGE_URL % 2)

            def should_be_null(self, topic):
                expect(topic).to_be_null()

        class CanStoreCrypto(Vows.Context):
            def topic(self):
                config = Config(REDIS_STORAGE_SERVER_PORT=7778, STORES_CRYPTO_KEY_FOR_EACH_IMAGE=True)
                storage = RedisStorage(Context(config=config, server=get_server('ACME-SEC')))

                storage.put(IMAGE_URL % 2, IMAGE_BYTES)
                storage.put_crypto(IMAGE_URL % 2)
                return storage.get_crypto(IMAGE_URL % 2)

            def should_not_be_null(self, topic):
                expect(topic).not_to_be_null()
                expect(topic).not_to_be_an_error()

            def should_have_proper_key(self, topic):
                expect(topic).to_equal('ACME-SEC')


