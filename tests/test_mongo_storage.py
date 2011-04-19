#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com
from os.path import join, abspath, dirname

from tornado.testing import AsyncHTTPTestCase
from tornado.options import options
from pymongo import Connection

import thumbor.loaders.http_loader as http
from thumbor.app import ThumborServiceApp
from thumbor.storages import mongo_storage

fixtures_folder = join(abspath(dirname(__file__)), 'fixtures')

connection = Connection('localhost', 27017)
collection = connection['thumbor_test']['images']

def rm_storage():
    connection.drop_database('thumbo_test')

class MongoStorageTest(AsyncHTTPTestCase):

    def get_app(self):
        return ThumborServiceApp(join(fixtures_folder, 'mongo_storage_conf.py'))

    def test_stores_image(self):
        rm_storage()
        options.STORES_CRYPTO_KEY_FOR_EACH_IMAGE = False
        image_url = 'www.globo.com/media/globocom/img/sprite1.png'
        http_loaded = http.load(image_url)
        storage = mongo_storage.Storage()
        storage.put(image_url, http_loaded)
        assert collection.find_one({'path': image_url}), 'image not found into the storage'
    
    def test_gets_image(self):
        rm_storage()
        options.STORES_CRYPTO_KEY_FOR_EACH_IMAGE = False
        image_url = 'www.globo.com/media/globocom/img/sprite1.png'
        http_loaded = http.load(image_url)
        storage = mongo_storage.Storage()
        storage.put(image_url, http_loaded)
        assert storage.get(image_url), 'image not found into the storage'

