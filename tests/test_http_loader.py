#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import urllib2

from tornado.testing import AsyncHTTPTestCase

import thumbor.loaders.http_loader as http
from thumbor.app import ThumborServiceApp

class HttpLoaderTest(AsyncHTTPTestCase):

    def get_app(self):
        return ThumborServiceApp()

    def test_loads_image(self):
        image_url = 'www.globo.com/media/globocom/img/sprite1.png'
        http_loaded = http.load(image_url)
        response = urllib2.urlopen('http://' + image_url).read()

        self.assertEqual(http_loaded, response, 'http_loaded is not the same as the http request')

    def test_verify_size(self):
        image_url = 'www.globo.com/media/globocom/img/sprite1.png'

        is_valid = http.verify_size(image_url, 1)

        assert not is_valid
