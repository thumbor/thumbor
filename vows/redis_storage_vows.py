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
from fixtures.redis_storage_fixture import IMAGE_URL, IMAGE_BYTES

class RedisDBContext(Vows.Context):
    def setup(self):
        self.connection = redis.Redis(port=6379,
                                      host='localhost',
                                      db=0)

@Vows.batch
class RedisStorageVows(RedisDBContext):
    class CanStoreImage(Vows.Context):
        def topic(self):
            storage = RedisStorage(Context(config=Config()))
            storage.put(IMAGE_URL % 1, IMAGE_BYTES)
            return self.parent.connection.get(IMAGE_URL % 1)

        def should_be_in_catalog(self, topic):
            expect(topic).not_to_be_null()
            expect(topic).not_to_be_an_error()

    class CanGetImage(Vows.Context):
        def topic(self):
            storage = RedisStorage(Context(config=Config()))
            storage.put(IMAGE_URL % 2, IMAGE_BYTES)
            return storage.get(IMAGE_URL % 2)

        def should_not_be_null(self, topic):
            expect(topic).not_to_be_null()
            expect(topic).not_to_be_an_error()

        def should_have_proper_bytes(self, topic):
            expect(topic).to_equal(IMAGE_BYTES)

