#!/usr/bin/env python
#-*- coding: utf8 -*-

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
