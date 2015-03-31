#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from datetime import datetime, timedelta
from cStringIO import StringIO

from pymongo import Connection
import gridfs

from thumbor.storages import BaseStorage
from tornado.concurrent import return_future


class Storage(BaseStorage):

    def __conn__(self):
        connection = Connection(
            self.context.config.MONGO_STORAGE_SERVER_HOST,
            self.context.config.MONGO_STORAGE_SERVER_PORT
        )

        db = connection[self.context.config.MONGO_STORAGE_SERVER_DB]
        storage = db[self.context.config.MONGO_STORAGE_SERVER_COLLECTION]

        return connection, db, storage

    def put(self, path, bytes):
        connection, db, storage = self.__conn__()

        doc = {
            'path': path,
            'created_at': datetime.now()
        }

        doc_with_crypto = dict(doc)
        if self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            if not self.context.server.security_key:
                raise RuntimeError("STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be True if no SECURITY_KEY specified")
            doc_with_crypto['crypto'] = self.context.server.security_key

        fs = gridfs.GridFS(db)
        file_data = fs.put(StringIO(bytes), **doc)

        doc_with_crypto['file_id'] = file_data
        storage.insert(doc_with_crypto)
        return path

    def put_crypto(self, path):
        if not self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            return

        connection, db, storage = self.__conn__()

        if not self.context.server.security_key:
            raise RuntimeError("STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be True if no SECURITY_KEY specified")

        crypto = storage.find_one({'path': path})

        crypto['crypto'] = self.context.server.security_key
        storage.update({'path': path}, crypto)
        return path

    def put_detector_data(self, path, data):
        connection, db, storage = self.__conn__()

        storage.update({'path': path}, {"$set": {"detector_data": data}})
        return path

    @return_future
    def get_crypto(self, path, callback):
        connection, db, storage = self.__conn__()

        crypto = storage.find_one({'path': path})
        callback(crypto.get('crypto') if crypto else None)

    @return_future
    def get_detector_data(self, path, callback):
        connection, db, storage = self.__conn__()

        doc = storage.find_one({'path': path})
        callback(doc.get('detector_data') if doc else None)

    @return_future
    def get(self, path, callback):
        connection, db, storage = self.__conn__()

        stored = storage.find_one({'path': path})

        if not stored or self.__is_expired(stored):
            callback(None)
            return

        fs = gridfs.GridFS(db)

        contents = fs.get(stored['file_id']).read()

        callback(str(contents))

    @return_future
    def exists(self, path, callback):
        connection, db, storage = self.__conn__()

        stored = storage.find_one({'path': path})

        if not stored or self.__is_expired(stored):
            callback(False)
        else:
            callback(True)

    def remove(self, path):
        if not self.exists(path):
            return

        connection, db, storage = self.__conn__()
        storage.remove({'path': path})

    def __is_expired(self, stored):
        timediff = datetime.now() - stored.get('created_at')
        return timediff > timedelta(seconds=self.context.config.STORAGE_EXPIRATION_SECONDS)
