#!/usr/bin/env python
#-*- coding: utf8 -*-

from os.path import join, abspath, dirname, exists

from tornado.testing import AsyncHTTPTestCase

import thumbor.loaders.http_loader as http
from thumbor.app import ThumborServiceApp
from thumbor.storages import file_storage


fixtures_folder = join(abspath(dirname(__file__)), 'fixtures')


class HttpLoaderTest(AsyncHTTPTestCase):
    
    def setup(self):
        storage_root = '/tmp/thumbor/storage'
        if exists(storage_root):
            os.rmdir(storage_root)
    
    def get_app(self):
        return ThumborServiceApp(join(fixtures_folder, 'file_storage_conf.py'))

    def test_loads_image(self):
        image_url = 'www.globo.com/media/globocom/img/sprite1.png'
        http_loaded = http.load(image_url)
        file_storage.put(http.resolve(image_url), http_loaded)
        assert exists('/tmp/thumbor/storage/media/globocom/img/sprite1.png'), 'image not found into the storage'
