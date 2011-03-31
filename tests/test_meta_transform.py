#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import unittest
from os.path import abspath, dirname, join
import json

from tornado.testing import AsyncHTTPTestCase

from thumbor.app import ThumborServiceApp

get_conf_path = lambda filename: abspath(join(dirname(__file__), 'fixtures', filename))

class MetaHandlerTestCase(AsyncHTTPTestCase):

    def get_app(self):
        return ThumborServiceApp(get_conf_path('default.py'))

    def test_meta_returns_200(self):
        self.http_client.fetch(self.get_url('/meta/s.glbimg.com/es/ge/f/original/2011/03/22/boavista_x_botafogo.jpg'), self.stop)
        response = self.wait()

        self.assertEqual(200, response.code)

    def test_meta_returns_appjson_code(self):
        self.http_client.fetch(self.get_url('/meta/s.glbimg.com/es/ge/f/original/2011/03/22/boavista_x_botafogo.jpg'), self.stop)
        response = self.wait()

        content_type = response.headers['Content-Type']
        self.assertEqual("application/json", content_type)

    def test_meta_returns_proper_json_for_no_ops(self):
        image_url = "s.glbimg.com/es/ge/f/original/2011/03/22/boavista_x_botafogo.jpg"
        self.http_client.fetch(self.get_url('/meta/%s' % image_url), self.stop)
        response = self.wait()

        text = response.body
        operations = json.loads(text)

        assert operations
        assert operations['thumbor']
        assert operations['thumbor']['source']['url'] == image_url
        assert operations['thumbor']['source']['width'] == 620
        assert operations['thumbor']['source']['height'] == 349
        assert "operations" in operations['thumbor']
        assert not operations['thumbor']['operations']

    def test_meta_returns_proper_json_for_resize_and_crop(self):
        image_url = "s.glbimg.com/es/ge/f/original/2011/03/22/boavista_x_botafogo.jpg"
        self.http_client.fetch(self.get_url('/meta/300x200/%s' % image_url), self.stop)
        response = self.wait()

        text = response.body
        thumbor_json = json.loads(text)

        operations = thumbor_json['thumbor']['operations']

        assert len(operations) == 2

        assert operations[0]['type'] == 'crop'
        assert operations[0]['top'] == 0
        assert operations[0]['right'] == 572
        assert operations[0]['bottom'] == 349
        assert operations[0]['left'] == 48

        assert operations[1]['type'] == 'resize'
        assert operations[1]['width'] == 300
        assert operations[1]['height'] == 200

    def test_meta_returns_proper_json_for_flip(self):
        image_url = "s.glbimg.com/es/ge/f/original/2011/03/22/boavista_x_botafogo.jpg"
        self.http_client.fetch(self.get_url('/meta/-300x-200/%s' % image_url), self.stop)
        response = self.wait()

        text = response.body
        thumbor_json = json.loads(text)

        operations = thumbor_json['thumbor']['operations']

        assert len(operations) == 4

        assert operations[2]['type'] == 'flip_horizontally'
        assert operations[3]['type'] == 'flip_vertically'

