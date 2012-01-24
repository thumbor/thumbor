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
        self.storage = MongoStorage(Context(config=Config()))
        self.fixtures_folder = join(abspath(dirname(__file__)), 'fixtures')

        self.connection = Connection('localhost', 27017)
        self.collection = self.connection['thumbor']['images']

    def teardown(self):
        self.connection.drop_database('thumbor')

@Vows.batch
class MongoStorageVows(MongoDBContext):
    class CanStoreImage(Vows.Context):
        def topic(self):
            self.parent.storage.put(IMAGE_URL, IMAGE_BYTES)
            return self.parent.collection.find_one({'path': IMAGE_URL})

        def should_be_in_catalog(self, topic):
            expect(topic).not_to_be_null()
            expect(topic).not_to_be_an_error()

