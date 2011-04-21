#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com
import datetime
import time
from os.path import join, abspath, dirname

from tornado.testing import AsyncHTTPTestCase
from tornado.options import options
from pymongo import Connection

import thumbor.loaders.http_loader as http
from thumbor.app import ThumborServiceApp
from thumbor.storages.mongo_storage import Storage

fixtures_folder = join(abspath(dirname(__file__)), 'fixtures')

connection = Connection('localhost', 27017)
collection = connection['thumbor_test']['images']

def rm_storage():
    connection.drop_database('thumbor_test')

class StorageTest(AsyncHTTPTestCase):

    def get_app(self):
        return ThumborServiceApp(join(fixtures_folder, 'mongo_storage_conf.py'))

    def test_stores_image(self):
        rm_storage()
        options.STORES_CRYPTO_KEY_FOR_EACH_IMAGE = False
        image_url = 'www.globo.com/media/globocom/img/sprite1.png'
        http_loaded = http.load(image_url)
        storage = Storage()
        storage.put(image_url, http_loaded)
        assert collection.find_one({'path': image_url}), 'image not found into the storage'

    def test_gets_image(self):
        rm_storage()
        options.STORES_CRYPTO_KEY_FOR_EACH_IMAGE = False
        image_url = 'www.globo.com/media/globocom/img/sprite1.png'
        http_loaded = http.load(image_url)
        storage = Storage()
        storage.put(image_url, http_loaded)
        stored_image = storage.get(image_url)
        assert stored_image and not isinstance(stored_image, dict), 'image not found into the storage'
        assert http_loaded == stored_image, 'stored image did not match the loaded one'

class StorageWithFalseStoreCryptoTest(AsyncHTTPTestCase):

    def get_app(self):
        return ThumborServiceApp(join(fixtures_folder, 'mongo_storage_conf.py'))

    def test_stores_image_does_not_store_crypt_key_if_not_in_options(self):
        rm_storage()
        options.STORES_CRYPTO_KEY_FOR_EACH_IMAGE = False
        image_url = 'www.globo.com/media/globocom/img/sprite1.png'
        http_loaded = http.load(image_url)
        storage = Storage()
        storage.put(image_url, http_loaded)
        assert not collection.find_one({'path': image_url}).has_key('crypto'), 'crypto key should not be found into the storage'

class StorageStoringCryptoKeyRaisesTest(AsyncHTTPTestCase):

    def get_app(self):
        return ThumborServiceApp(join(fixtures_folder, 'mongo_storage_conf.py'))

    def test_storing_an_empty_key_raises(self):
        rm_storage()
        options.SECURITY_KEY = False
        options.STORES_CRYPTO_KEY_FOR_EACH_IMAGE = True
        image_url = 'www.globo.com/media/globocom/img/sprite1.png'
        http_loaded = http.load(image_url)
        storage = Storage()

        try:
            storage.put(image_url, http_loaded)
        except RuntimeError, err:
            assert str(err) == "STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be True if no SECURITY_KEY specified"
            return

        assert False, "should not have gotten this far"

class StorageStoringCryptoKeyFindsSecurityFile(AsyncHTTPTestCase):

    def get_app(self):
        return ThumborServiceApp(join(fixtures_folder, 'mongo_storage_conf.py'))

    def test_finding_crypto_file(self):
        rm_storage()
        options.STORES_CRYPTO_KEY_FOR_EACH_IMAGE = True
        options.SECURITY_KEY = 'MY-SECURITY-KEY'
        image_url = 'www.globo.com/media/globocom/img/sprite1.png'
        http_loaded = http.load(image_url)
        storage = Storage()

        storage.put(image_url, http_loaded)

        stored_crypto_key = collection.find_one({'path': image_url}).get('crypto')
        assert stored_crypto_key == options.SECURITY_KEY, '%s crypto key should be equal %s' % (stored_crypto_key, options.SECURITY_KEY)
    def test_get_crypto_for_url(self):
        rm_storage()
        image_url = 'www.globo.com/media/globocom/img/sprite1.png'
        http_loaded = http.load(image_url)
        storage = Storage()

        storage.put(image_url, http_loaded)

        assert storage.get_crypto(image_url) == options.SECURITY_KEY

    def test_get_crypto_for_url_returns_None_if_urls_was_never_seen(self):
        rm_storage()
        image_url = 'www.globo.com/media/globocom/img/sprite1.png'
        storage = Storage()

        assert not storage.get_crypto(image_url)


class StorageExpirationTime(AsyncHTTPTestCase):

    def get_app(self):
        return ThumborServiceApp(join(fixtures_folder, 'mongo_storage_conf.py'))

    def test_before_expiration_returns_something(self):
        rm_storage()
        options.STORAGE_EXPIRATION_SECONDS = 1000
        image_url = 'www.globo.com/media/globocom/img/sprite1.png'
        http_loaded = http.load(image_url)
        storage = Storage()
        storage.put(image_url, http_loaded)
        assert storage.get(image_url)

    def test_after_expiration_returns_none(self):
        rm_storage()
        options.STORAGE_EXPIRATION_SECONDS = 1
        image_url = 'www.globo.com/media/globocom/img/sprite1.png'
        http_loaded = http.load(image_url)
        storage = Storage()
        storage.put(image_url, http_loaded)
        time.sleep(2)
        assert storage.get(image_url) is None

