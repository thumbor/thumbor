#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import tempfile
from os.path import join, abspath, dirname

from tornado.testing import AsyncHTTPTestCase

import thumbor.loaders.file_loader as file_loader
from thumbor.app import ThumborServiceApp

fixtures_folder = join(abspath(dirname(__file__)), 'fixtures')

class FileLoaderTest(AsyncHTTPTestCase):

    def get_app(self):
        conf = open(join(fixtures_folder, 'file_loader_conf.py')).read()
        conf = conf.replace(r'@@rootdir@@', fixtures_folder)
        conf_file = tempfile.NamedTemporaryFile(mode='w+b', dir='/tmp', delete=False)
        conf_file.write(conf)
        conf_file.close()
        return ThumborServiceApp(conf_file.name)

    def test_loads_image(self):
        image_url = 'img/fixture1.png'
        file_loaded = file_loader.load(image_url)
        response = open(join(fixtures_folder, 'img', 'fixture1.png')).read()

        self.assertEqual(file_loaded, response, 'file_loaded is not the same as the filesystem equivalent')
