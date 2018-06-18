#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from os.path import abspath, join, dirname

from unittest import TestCase
from preggy import expect

from thumbor.context import Context
from thumbor.config import Config
from thumbor.loaders.file_loader import load
from thumbor.loaders import LoaderResult

STORAGE_PATH = abspath(join(dirname(__file__), '../fixtures/images/'))


class FileLoaderTestCase(TestCase):
    def setUp(self):
        config = Config(FILE_LOADER_ROOT_PATH=STORAGE_PATH)
        self.ctx = Context(config=config)

    def load_file(self, file_name):
        return load(self.ctx, file_name, lambda x: x).result()

    def test_should_load_file(self):
        result = self.load_file('image.jpg')
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal(
            open(join(STORAGE_PATH, 'image.jpg')).read())
        expect(result.successful).to_be_true()

    def test_should_fail_when_inexistent_file(self):
        result = self.load_file('image_NOT.jpg')
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal(None)
        expect(result.successful).to_be_false()

    def test_should_fail_when_outside_root_path(self):
        result = self.load_file('../__init__.py')
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal(None)
        expect(result.successful).to_be_false()

    def test_should_load_file_with_spaces_in_name(self):
        result = self.load_file('image .jpg')
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal(
            open(join(STORAGE_PATH, 'image.jpg')).read())
        expect(result.successful).to_be_true()

    def test_should_load_file_with_spaces_encoded_in_name(self):
        result = self.load_file('image2%20.jpg')
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal(
            open(join(STORAGE_PATH, 'image2%20.jpg')).read())
        expect(result.successful).to_be_true()
