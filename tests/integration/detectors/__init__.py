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


class DetectorTestCase(TestCase):
    '''TestCase base class for all detector tests'''

    def get_detector_blueprint(self):  # pylint: disable=no-self-use
        '''Gets the detector blueprint full name for this test case'''
        assert False, 'Must be overriden in the test case'

    @property
    def fixture_path(self):
        '''Returns the fixtures path'''
        return join(
            dirname(realpath(__file__)), '..', '..', 'fixtures', 'detectors')

    def get_config(self):
        detect_bp = self.get_detector_blueprint()
        fullname = f'{detect_bp.__name__}'
        return Config(
            BLUEPRINTS=[
                'thumbor.blueprints.loaders.file',
                'thumbor.blueprints.engines.pillow',
                fullname,
            ],
            FILE_LOADER_ROOT_PATH=self.fixture_path)

    @gen.coroutine
    def smart_detect(self, source_image, width=300, height=200):
        'Get smart detect image bytes'
        image = yield self.get(
            f'/unsafe/{width}x{height}/smart/{source_image}')
        return image.body
