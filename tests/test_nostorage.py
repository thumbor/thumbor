#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import join, abspath, dirname

from tornado.testing import AsyncHTTPTestCase

import thumbor.loaders.http_loader as http
from thumbor.app import ThumborServiceApp
from thumbor.storages import no_storage 

fixtures_folder = join(abspath(dirname(__file__)), 'fixtures')

class FileStorageTest(AsyncHTTPTestCase):

    def get_app(self):
        return ThumborServiceApp(join(fixtures_folder, 'no_storage_conf.py'))

    def test_stores_image_does_nothing(self):
        image_url = 'www.globo.com/media/globocom/img/sprite1.png'
        http_loaded = http.load(image_url)
        storage = no_storage.Storage()
        storage.put(image_url, http_loaded)

    def test_no_storage_returns_false_in_exists(self):
        image_url = 'www.globo.com/media/globocom/img/sprite1.png'
        storage = no_storage.Storage()
        assert not storage.get(image_url)
