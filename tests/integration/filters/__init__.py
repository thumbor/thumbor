#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from os.path import realpath, dirname, join

import tornado.gen as gen

from thumbor.config import Config
from tests.integration import TestCase


class FilterTestCase(TestCase):
    '''TestCase base class for all filter tests'''

    def get_filter(self):  # pylint: disable=no-self-use
        '''Gets the filter full name for this test case'''
        assert False, 'Must be overriden in the test case'

    @property
    def fixture_path(self):
        '''Returns the fixtures path'''
        return join(
            dirname(realpath(__file__)), '..', '..', 'fixtures', 'filters')

    def get_config(self):
        return Config(
            FILTERS=[self.get_filter().__module__],
            BLUEPRINTS=[
                'thumbor.blueprints.loaders.file',
                'thumbor.blueprints.storages.file',
                'thumbor.blueprints.engines.pillow',
            ],
            FILE_LOADER_ROOT_PATH=self.fixture_path)

    @gen.coroutine
    def get_filtered(self, filter_str, source_image, pre_path='/unsafe/'):
        'Get filtered image bytes'
        image = yield self.get(
            f'{pre_path}filters:{filter_str}/{source_image}')
        return image.body
