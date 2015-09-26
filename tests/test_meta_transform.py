#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import abspath, dirname, join
import json

from tornado.testing import AsyncHTTPTestCase
from tornado.options import options

from thumbor.app import ThumborServiceApp

get_conf_path = lambda filename: abspath(join(dirname(__file__), 'fixtures', filename))


class MetaHandlerTestCase(AsyncHTTPTestCase):

    def get_app(self):
        app = ThumborServiceApp(get_conf_path('default.py'))
        return app

    def test_meta_returns_200(self):
        options.META_CALLBACK_NAME = None
        self.http_client.fetch(self.get_url('/unsafe/meta/s.glbimg.com/es/ge/f/original/2011/03/22/boavista_x_botafogo.jpg'), self.stop)
        response = self.wait()

        self.assertEqual(200, response.code)

    def test_meta_returns_appjson_code(self):
        options.META_CALLBACK_NAME = None
        self.http_client.fetch(self.get_url('/unsafe/meta/s.glbimg.com/es/ge/f/original/2011/03/22/boavista_x_botafogo.jpg'), self.stop)
        response = self.wait()

        assert response.code == 200
        content_type = response.headers['Content-Type']
        self.assertEqual("application/json", content_type)

    def test_meta_returns_proper_json_for_no_ops(self):
        options.META_CALLBACK_NAME = None
        image_url = "s.glbimg.com/es/ge/f/original/2011/03/22/boavista_x_botafogo.jpg"
        self.http_client.fetch(self.get_url('/unsafe/meta/%s' % image_url), self.stop)
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
        options.META_CALLBACK_NAME = None
        image_url = "s.glbimg.com/es/ge/f/original/2011/03/22/boavista_x_botafogo.jpg"
        self.http_client.fetch(self.get_url('/unsafe/meta/300x200/%s' % image_url), self.stop)
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

    def test_meta_returns_proper_json_for_resize_and_manual_crop(self):
        options.META_CALLBACK_NAME = None
        image_url = "s.glbimg.com/es/ge/f/original/2011/03/22/boavista_x_botafogo.jpg"
        self.http_client.fetch(self.get_url('/unsafe/meta/0x0:100x100/50x0/%s' % image_url), self.stop)
        response = self.wait()

        text = response.body
        thumbor_json = json.loads(text)

        target = thumbor_json['thumbor']['target']

        assert target['width'] == 50
        assert target['height'] == 50, target['height']

    def test_meta_returns_proper_target_for_resize_and_crop(self):
        options.META_CALLBACK_NAME = None
        image_url = "s.glbimg.com/es/ge/f/original/2011/03/22/boavista_x_botafogo.jpg"
        self.http_client.fetch(self.get_url('/unsafe/meta/300x200/%s' % image_url), self.stop)
        response = self.wait()

        text = response.body
        thumbor_json = json.loads(text)

        target = thumbor_json['thumbor']['target']

        assert target['width'] == 300
        assert target['height'] == 200

    def test_meta_returns_proper_target_for_crop(self):
        options.META_CALLBACK_NAME = None
        image_url = "s.glbimg.com/es/ge/f/original/2011/03/22/boavista_x_botafogo.jpg"
        self.http_client.fetch(self.get_url('/unsafe/meta/0x0:100x100/%s' % image_url), self.stop)
        response = self.wait()

        text = response.body
        thumbor_json = json.loads(text)

        target = thumbor_json['thumbor']['target']

        assert target['width'] == 100
        assert target['height'] == 100

    def test_meta_returns_proper_target_for_crop_and_resize(self):
        options.META_CALLBACK_NAME = None
        image_url = "s.glbimg.com/es/ge/f/original/2011/03/22/boavista_x_botafogo.jpg"
        self.http_client.fetch(self.get_url('/unsafe/meta/0x0:200x250/200x0/%s' % image_url), self.stop)
        response = self.wait()

        text = response.body
        thumbor_json = json.loads(text)

        target = thumbor_json['thumbor']['target']

        image_url = "s.glbimg.com/es/ge/f/original/2011/03/22/boavista_x_botafogo.jpg"
        self.http_client.fetch(self.get_url('/unsafe/meta/50x40:250x290/200x0/%s' % image_url), self.stop)
        response = self.wait()

        text = response.body
        thumbor_json = json.loads(text)

        target_2 = thumbor_json['thumbor']['target']

        image_url = "s.glbimg.com/es/ge/f/original/2011/03/22/boavista_x_botafogo.jpg"
        self.http_client.fetch(self.get_url('/unsafe/meta/250x80:450x330/200x0/%s' % image_url), self.stop)
        response = self.wait()

        text = response.body
        thumbor_json = json.loads(text)

        target_3 = thumbor_json['thumbor']['target']

        assert target['width'] == target_2['width']
        assert target['height'] == target_2['height']

        assert target['width'] == target_3['width']
        assert target['height'] == target_3['height']

    def test_meta_returns_proper_json_for_flip(self):
        options.META_CALLBACK_NAME = None
        image_url = "s.glbimg.com/es/ge/f/original/2011/03/22/boavista_x_botafogo.jpg"
        self.http_client.fetch(self.get_url('/unsafe/meta/-300x-200/%s' % image_url), self.stop)
        response = self.wait()

        text = response.body
        thumbor_json = json.loads(text)

        operations = thumbor_json['thumbor']['operations']

        assert len(operations) == 4

        assert operations[2]['type'] == 'flip_horizontally'
        assert operations[3]['type'] == 'flip_vertically'


class MetaHandlerJSONPTestCase(AsyncHTTPTestCase):

    def get_app(self):
        return ThumborServiceApp(get_conf_path('jsonp.py'))

    def test_meta_returns_proper_json_for_no_ops_with_callback(self):
        image_url = "s.glbimg.com/es/ge/f/original/2011/03/22/boavista_x_botafogo.jpg"
        self.http_client.fetch(self.get_url('/unsafe/meta/%s' % image_url), self.stop)
        response = self.wait()

        text = response.body

        assert text.strip().startswith('callback({')
        assert text.strip().endswith('});')
