#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com
from pymongo import Connection
from tornado.options import options, define

from thumbor.storages import BaseStorage

define('MONGO_STORAGE_SERVER_HOST', type=str, default='localhost')
define('MONGO_STORAGE_SERVER_PORT', type=int, default=27017)
define('MONGO_STORAGE_SERVER_DB', type=str, default='thumbor')
define('MONGO_STORAGE_SERVER_COLLECTION', type=str, default='images')

class Storage(BaseStorage):

    def __init__(self):
        self.connection = Connection(options.MONGO_STORAGE_SERVER_HOST, options.MONGO_STORAGE_SERVER_PORT)
        self.db = self.connection[options.MONGO_STORAGE_SERVER_DB]
        self.storage = self.db[options.MONGO_STORAGE_SERVER_COLLECTION]

    def put(self, path, bytes):
        self.storage.insert({'path': path, 'bytes': bytes})

    def get_crypto(self, path):
        pass

    def get(self, path):
        return self.storage.find_one({'path': path})


