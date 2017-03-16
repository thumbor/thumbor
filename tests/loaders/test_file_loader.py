#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import tornado

from os.path import abspath, join, dirname

from preggy import expect

from thumbor.context import Context
from thumbor.config import Config
from thumbor.loaders.file_loader import load
from thumbor.loaders import LoaderResult

from tests.base import TestCase

STORAGE_PATH = abspath(join(dirname(__file__), '../fixtures/images/'))


class FileLoaderTestCase(TestCase):

    def setUp(self):
        super(FileLoaderTestCase, self).setUp()
        config = Config(
            FILE_LOADER_ROOT_PATH=STORAGE_PATH
        )
        self.ctx = Context(config=config)

    @tornado.testing.gen_test
    def test_should_load_file(self):
        result = yield load(self.ctx, 'image.jpg')
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal(open(join(STORAGE_PATH, 'image.jpg')).read())
        expect(result.successful).to_be_true()

    @tornado.testing.gen_test
    def test_should_fail_when_inexistent_file(self):
        result = yield load(self.ctx, 'image_NOT.jpg')
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal(None)
        expect(result.successful).to_be_false()

    @tornado.testing.gen_test
    def test_should_fail_when_outside_root_path(self):
        result = yield load(self.ctx, '../__init__.py')
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal(None)
        expect(result.successful).to_be_false()
