#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import join, abspath, dirname, exists

from tornado.testing import AsyncHTTPTestCase

import thumbor.loaders.http_loader as http
from thumbor.app import ThumborServiceApp
from thumbor.storages import file_storage

fixtures_folder = join(abspath(dirname(__file__)), 'fixtures')

class FileStorageTest(AsyncHTTPTestCase):

    def setup(self):
        storage_root = '/tmp/thumbor/storage'
        if exists(storage_root):
            os.rmdir(storage_root)

    def get_app(self):
        return ThumborServiceApp(join(fixtures_folder, 'file_storage_conf.py'))

    def test_stores_image(self):
        image_url = 'www.globo.com/media/globocom/img/sprite1.png'
        http_loaded = http.load(image_url)
        storage = file_storage.Storage()
        storage.put(image_url, http_loaded)
        assert exists('/tmp/thumbor/storage/www.globo.com/media/globocom/img/sprite1.png'), 'image not found into the storage'
