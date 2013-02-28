#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import os
from os.path import join, abspath, dirname
from io import StringIO
import unittest

from PIL import Image
from tornado.testing import AsyncHTTPTestCase

from thumbor.app import ThumborServiceApp

get_conf_path = lambda filename: abspath(join(os.environ.get('test_path', dirname(__file__)), 'fixtures', filename))


class MainHandlerSourcePathTest(AsyncHTTPTestCase):

    def get_app(self):
        return ThumborServiceApp(get_conf_path('conf1.py'))

    def test_validates_passed_url_is_in_valid_source(self):
        self.http_client.fetch(self.get_url('/unsafe/www.mydomain.com/logo2.jpg'), self.stop)
        response = self.wait()
        self.assertEqual(404, response.code)


class MainHandlerTest(AsyncHTTPTestCase):

    def get_app(self):
        return ThumborServiceApp(get_conf_path('default.py'))

    def test_returns_success_status_code(self):
        self.http_client.fetch(self.get_url('/unsafe/www.globo.com/media/globocom/img/sprite1.png'), self.stop)
        response = self.wait(timeout=20)
        self.assertEqual(200, response.code)


class ImageTestCase(AsyncHTTPTestCase):

    def get_app(self):
        return ThumborServiceApp(get_conf_path('default.py'))

    def fetch_image(self, url):
        self.http_client.fetch(self.get_url(url), self.stop)
        response = self.wait()
        self.assertEqual(200, response.code)
        return Image.open(StringIO(response.body))


class MainHandlerImagesTest(ImageTestCase):

    def test_resizes_the_passed_image(self):
        image = self.fetch_image('/unsafe/200x300/www.globo.com/media/globocom/img/sprite1.png')
        img_width, img_height = image.size
        self.assertEqual(img_width, 200)
        self.assertEqual(img_height, 300)

    def test_flips_horizontaly_the_passed_image(self):
        image = self.fetch_image('/unsafe/www.globo.com/media/common/img/estrutura/borderbottom.gif')
        image_flipped = self.fetch_image('/unsafe/-3x/www.globo.com/media/common/img/estrutura/borderbottom.gif')
        pixels = list(image.getdata())
        pixels_flipped = list(image_flipped.getdata())

        self.assertEqual(len(pixels), len(pixels_flipped), 'the images do not have the same size')

        reversed_pixels_flipped = list(reversed(pixels_flipped))

        self.assertEqual(pixels, reversed_pixels_flipped, 'did not flip the image')


class MainHandlerFitInImagesTest(ImageTestCase):

    def test_fits_in_image_horizontally(self):
        #620x470
        image = self.fetch_image('/unsafe/fit-in/200x300/s.glbimg.com/es/ge/f/original/2011/04/19/adriano_ae62.jpg')

        width, height = image.size

        assert width == 200, width
        assert height == 151, height

if __name__ == '__main__':
    unittest.main()
