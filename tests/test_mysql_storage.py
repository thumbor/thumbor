#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import time
from os.path import join, abspath, dirname

from tornado.testing import AsyncHTTPTestCase
from tornado.options import options
import MySQLdb as mysql

import thumbor.loaders.http_loader as http
from thumbor.app import ThumborServiceApp
from thumbor.storages.mysql_storage import Storage

fixtures_folder = join(abspath(dirname(__file__)), 'fixtures')

def get_image_by_path(image_url):
    db = mysql.connect(host="localhost", user="root", passwd="", db="thumbor_tests")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM images where url=%s", image_url)

    register = cursor.fetchone()
    if not register:
        return None
    return {
        'url': register[0],
        'contents': register[1],
        'security_key': register[2],
        'last_update': register[3]
    }
    db.close()

class StorageTest(AsyncHTTPTestCase):

    def get_app(self):
        return ThumborServiceApp(join(fixtures_folder, 'mysql_storage_conf.py'))

    def test_stores_image(self):
        options.STORES_CRYPTO_KEY_FOR_EACH_IMAGE = False
        image_url = 'www.globo.com/media/globocom/img/sprite1.png?1'
        http_loaded = http.load(image_url)
        storage = Storage()
        storage.put(image_url, http_loaded)

        image = get_image_by_path(image_url)
        assert image['url'] == image_url
        assert image['contents']
        assert image['last_update']

    def test_gets_image(self):
        options.STORES_CRYPTO_KEY_FOR_EACH_IMAGE = False
        image_url = 'www.globo.com/media/globocom/img/sprite1.png?2'
        http_loaded = http.load(image_url)
        storage = Storage()
        storage.put(image_url, http_loaded)
        stored_image = storage.get(image_url)
        assert stored_image and not isinstance(stored_image, dict), 'image not found into the storage'
        assert http_loaded == stored_image, 'stored image did not match the loaded one'

class StorageWithFalseStoreCryptoTest(AsyncHTTPTestCase):

    def get_app(self):
        return ThumborServiceApp(join(fixtures_folder, 'mysql_storage_conf.py'))

    def test_stores_image_does_not_store_crypt_key_if_not_in_options(self):
        options.STORES_CRYPTO_KEY_FOR_EACH_IMAGE = False
        image_url = 'www.globo.com/media/globocom/img/sprite1.png?3'
        http_loaded = http.load(image_url)
        storage = Storage()
        storage.put(image_url, http_loaded)

        image = get_image_by_path(image_url)

        assert not image['security_key']

class StorageStoringCryptoKeyRaisesTest(AsyncHTTPTestCase):

    def get_app(self):
        return ThumborServiceApp(join(fixtures_folder, 'mysql_storage_conf.py'))

    def test_storing_an_empty_key_raises(self):
        options.SECURITY_KEY = False
        options.STORES_CRYPTO_KEY_FOR_EACH_IMAGE = True
        image_url = 'www.globo.com/media/globocom/img/sprite1.png?4'
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
        return ThumborServiceApp(join(fixtures_folder, 'mysql_storage_conf.py'))

    def test_finding_crypto_file(self):
        options.STORES_CRYPTO_KEY_FOR_EACH_IMAGE = True
        options.SECURITY_KEY = 'MY-SECURITY-KEY-5'
        image_url = 'www.globo.com/media/globocom/img/sprite1.png?5'
        http_loaded = http.load(image_url)
        storage = Storage()

        storage.put(image_url, http_loaded)

        image = get_image_by_path(image_url)

        assert image['security_key'] == options.SECURITY_KEY

    def test_get_crypto_for_url(self):
        image_url = 'www.globo.com/media/globocom/img/sprite1.png?6'
        http_loaded = http.load(image_url)
        storage = Storage()

        storage.put(image_url, http_loaded)

        assert storage.get_crypto(image_url) == options.SECURITY_KEY

    def test_get_crypto_for_url_returns_None_if_urls_was_never_seen(self):
        image_url = 'www.globo.com/media/globocom/img/sprite1.png?7'
        storage = Storage()
        assert not storage.get_crypto(image_url)


class StorageExpirationTime(AsyncHTTPTestCase):

    def get_app(self):
        return ThumborServiceApp(join(fixtures_folder, 'mysql_storage_conf.py'))

    def test_before_expiration_returns_something(self):
        options.STORAGE_EXPIRATION_SECONDS = 1000
        image_url = 'www.globo.com/media/globocom/img/sprite1.png?8'
        http_loaded = http.load(image_url)
        storage = Storage()
        storage.put(image_url, http_loaded)
        assert storage.get(image_url)

    def test_after_expiration_returns_none(self):
        options.STORAGE_EXPIRATION_SECONDS = 1
        image_url = 'www.globo.com/media/globocom/img/sprite1.png?9'
        http_loaded = http.load(image_url)
        storage = Storage()
        storage.put(image_url, http_loaded)
        time.sleep(2)
        assert storage.get(image_url) is None

