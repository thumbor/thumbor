#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import abspath, join, dirname

from pymongo import Connection
from pyvows import Vows, expect

from thumbor.storages.mongo_storage import Storage as MongoStorage
from thumbor.context import Context
from thumbor.config import Config
from fixtures.mongo_storage_fixture import IMAGE_URL, IMAGE_BYTES

class MongoDBContext(Vows.Context):
    def setup(self):
        self.fixtures_folder = join(abspath(dirname(__file__)), 'fixtures')

        self.connection = Connection('localhost', 27017)
        self.collection = self.connection['thumbor']['images']

    def teardown(self):
        self.connection.drop_database('thumbor')

@Vows.batch
class MongoStorageVows(MongoDBContext):
    class CanStoreImage(Vows.Context):
        def topic(self):
            storage = MongoStorage(Context(config=Config()))
            storage.put(IMAGE_URL % 1, IMAGE_BYTES)
            return self.parent.collection.find_one({'path': IMAGE_URL % 1})

        def should_be_in_catalog(self, topic):
            expect(topic).not_to_be_null()
            expect(topic).not_to_be_an_error()

    class CanGetImage(Vows.Context):
        def topic(self):
            storage = MongoStorage(Context(config=Config()))
            storage.put(IMAGE_URL % 2, IMAGE_BYTES)
            return storage.get(IMAGE_URL % 2)

        def should_not_be_null(self, topic):
            expect(topic).not_to_be_null()
            expect(topic).not_to_be_an_error()

        def should_have_proper_bytes(self, topic):
            expect(topic).to_equal(IMAGE_BYTES)

    class StoresCrypto(Vows.Context):
        class DoesNotStoreWhenConfigIsFalseInPutMethod(Vows.Context):
            def topic(self):
                storage = MongoStorage(Context(config=Config(STORES_CRYPTO_KEY_FOR_EACH_IMAGE=False)))
                storage.put(IMAGE_URL % 3, IMAGE_BYTES)

                return self.parent.parent.collection.find_one({'path': IMAGE_URL % 3})

            def should_be_in_catalog(self, topic):
                expect(topic).not_to_be_null()
                expect(topic).not_to_be_an_error()

            def should_not_have_crypto_key(self, topic):
                expect(topic.has_key('crypto')).to_be_false()

        class StoringEmptyKeyRaises(Vows.Context):
            def topic(self):
                storage = MongoStorage(Context(config=Config(STORES_CRYPTO_KEY_FOR_EACH_IMAGE=True, SECURITY_KEY='')))
                storage.put(IMAGE_URL % 4, IMAGE_BYTES)

            def should_be_an_error(self, topic):
                expect(topic).to_be_an_error_like(RuntimeError)
                expect(topic).to_have_an_error_message_of("STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be True if no SECURITY_KEY specified")

        class StoringProperKey(Vows.Context):
            def topic(self):
                storage = MongoStorage(Context(config=Config(STORES_CRYPTO_KEY_FOR_EACH_IMAGE=True, SECURITY_KEY='ACME-SEC')))
                storage.put(IMAGE_URL % 5, IMAGE_BYTES)

                return self.parent.parent.collection.find_one({'path': IMAGE_URL % 5})

            def should_be_in_catalog(self, topic):
                expect(topic).not_to_be_null()
                expect(topic).not_to_be_an_error()

            def should_have_crypto_key(self, topic):
                expect(topic.has_key('crypto')).to_be_true()
                expect(topic['crypto']).to_equal('ACME-SEC')

