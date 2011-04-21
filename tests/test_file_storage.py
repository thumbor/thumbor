#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import time
import shutil
from os.path import join, abspath, dirname, exists

from tornado.testing import AsyncHTTPTestCase
from tornado.options import options

import thumbor.loaders.http_loader as http
from thumbor.app import ThumborServiceApp
from thumbor.storages import file_storage

fixtures_folder = join(abspath(dirname(__file__)), 'fixtures')

def rm_storage():
    storage_root = '/tmp/thumbor/storage'
    if exists(storage_root):
        shutil.rmtree(storage_root)

class FileStorageTest(AsyncHTTPTestCase):

    def get_app(self):
        return ThumborServiceApp(join(fixtures_folder, 'file_storage_conf.py'))

    def test_stores_image(self):
        rm_storage()
        options.STORES_CRYPTO_KEY_FOR_EACH_IMAGE = False
        image_url = 'www.globo.com/media/globocom/img/sprite1.png'
        http_loaded = http.load(image_url)
        storage = file_storage.Storage()
        storage.put(image_url, http_loaded)
        assert exists('/tmp/thumbor/storage/www.globo.com/media/globocom/img/sprite1.png'), 'image not found into the storage'

class FileStorageWithFalseStoreCryptoTest(AsyncHTTPTestCase):

    def get_app(self):
        return ThumborServiceApp(join(fixtures_folder, 'file_storage_conf.py'))

    def test_stores_image_does_not_store_crypt_key_if_not_in_options(self):
        rm_storage()
        options.STORES_CRYPTO_KEY_FOR_EACH_IMAGE = False
        image_url = 'www.globo.com/media/globocom/img/sprite1.png'
        http_loaded = http.load(image_url)
        storage = file_storage.Storage()
        storage.put(image_url, http_loaded)
        assert not exists('/tmp/thumbor/storage/www.globo.com/media/globocom/img/sprite1.txt'), 'crypto key was found into the storage'

class FileStorageStoringCryptoKeyRaisesTest(AsyncHTTPTestCase):

    def get_app(self):
        return ThumborServiceApp(join(fixtures_folder, 'file_storage_conf_2.py'))

    def test_storing_an_empty_key_raises(self):
        rm_storage()
        options.SECURITY_KEY = False
        image_url = 'www.globo.com/media/globocom/img/sprite1.png'
        http_loaded = http.load(image_url)
        storage = file_storage.Storage()

        try:
            storage.put(image_url, http_loaded)
        except RuntimeError, err:
            assert str(err) == "STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be True if no SECURITY_KEY specified"
            return

        assert False, "should not have gotten this far"

class FileStorageStoringCryptoKeyFindsSecurityFile(AsyncHTTPTestCase):

    def get_app(self):
        return ThumborServiceApp(join(fixtures_folder, 'file_storage_conf_3.py'))

    def test_finding_crypto_file(self):
        rm_storage()
        image_url = 'www.globo.com/media/globocom/img/sprite1.png'
        http_loaded = http.load(image_url)
        storage = file_storage.Storage()

        storage.put(image_url, http_loaded)

        crypto_file = '/tmp/thumbor/storage/www.globo.com/media/globocom/img/sprite1.txt'
        assert exists(crypto_file), 'crypto key was not found into the storage'

        assert file(crypto_file).read() == options.SECURITY_KEY

    def test_get_crypto_for_url(self):
        rm_storage()
        image_url = 'www.globo.com/media/globocom/img/sprite1.png'
        http_loaded = http.load(image_url)
        storage = file_storage.Storage()

        storage.put(image_url, http_loaded)

        assert storage.get_crypto(image_url) == options.SECURITY_KEY

    def test_get_crypto_for_url_returns_None_if_urls_was_never_seen(self):
        rm_storage()
        image_url = 'www.globo.com/media/globocom/img/sprite1.png'
        storage = file_storage.Storage()

        assert not storage.get_crypto(image_url)

class StorageExpirationTime(AsyncHTTPTestCase):

    def get_app(self):
        return ThumborServiceApp(join(fixtures_folder, 'file_storage_conf.py'))

    def test_before_expiration_returns_something(self):
        rm_storage()
        options.STORAGE_EXPIRATION_SECONDS = 1000
        image_url = 'www.globo.com/media/globocom/img/sprite1.png'
        http_loaded = http.load(image_url)
        storage = file_storage.Storage()
        storage.put(image_url, http_loaded)
        assert storage.get(image_url)

    def test_after_expiration_returns_none(self):
        rm_storage()
        options.STORAGE_EXPIRATION_SECONDS = 1
        image_url = 'www.globo.com/media/globocom/img/sprite1.png'
        http_loaded = http.load(image_url)
        storage = file_storage.Storage()
        storage.put(image_url, http_loaded)
        time.sleep(2)
        assert storage.get(image_url) is None


