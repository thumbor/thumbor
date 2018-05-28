#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from os.path import realpath, dirname, join
import random

from PIL import Image
import tornado.gen as gen

from thumbor.config import Config
from tests.integration import TestCase


class FilterTestCase(TestCase):
    '''TestCase base class for all filter tests'''

    def get_filter_name(self):
        '''Gets the filter full name for this test case'''
        assert False, 'Must be overriden in the test case'

    @property
    def fixture_path(self):
        return join(
            dirname(realpath(__file__)), '..', '..', 'fixtures', 'filters')

    def get_config(self):
        return Config(
            FILTERS=[self.get_filter_name()],
            BLUEPRINTS=[
                'thumbor.blueprints.loaders.file',
                'thumbor.blueprints.storages.file',
                'thumbor.blueprints.engines.pillow',
            ],
            FILE_LOADER_ROOT_PATH=self.fixture_path)

    def get_request_handler(self):  # pylint: disable=no-self-use
        'Gets default request handler. Can be overriden.'
        return None

    def get_fixture_path(self, name):
        'Returns a fixture path'
        return f'{self.fixture_path}/{name}'

    def get_fixture(self, name):
        'Gets a fixture image'
        image = Image.open(self.get_fixture_path(name))
        return image.convert('RGB')

    def debug(self, image):
        'Stores the image buffer in a temp file'
        image = Image.fromarray(image)
        path = '/tmp/debug_image_%s.jpg' % random.randint(1, 10000)
        image.save(path, 'JPEG')
        print('The debug image was in %s.' % path)

    def debug_size(self, image):
        'Prints the image dimensions'
        image = Image.fromarray(image)
        print("Image dimensions are %dx%d (shape is %s)" %
              (image.size[0], image.size[1], image.shape))

    @gen.coroutine
    def get_filtered(self, filter_str, source_image):
        image = yield self.get(
            f'/v2/unsafe/filters:{filter_str}/{source_image}')
        return image.body
