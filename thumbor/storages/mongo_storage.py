#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from datetime import datetime

from pymongo import Connection
from tornado.options import options, define
from bson.binary import Binary

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
        store = {
            'path': path,
            'bytes': Binary(bytes, 128),
            'created_at': datetime.now()
        }
        if options.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            if not options.SECURITY_KEY:
                raise RuntimeError("STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be True if no SECURITY_KEY specified")
            store['crypto'] = options.SECURITY_KEY
        
        self.storage.insert(store)

    def get_crypto(self, path):
        crypto = self.storage.find_one({'path': path})
        return crypto.get('crypto') if crypto else None

    def get(self, path):
        stored = self.storage.find_one({'path': path})

        if not stored or self.__is_expired(stored):
            return None

        return str(stored.get('bytes'))

    def __is_expired(self, stored):
        timediff = datetime.now() - stored.get('created_at')
        return timediff.seconds > options.STORAGE_EXPIRATION_SECONDS

