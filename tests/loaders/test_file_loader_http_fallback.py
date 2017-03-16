#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from functools import partial

from mock import patch
from preggy import expect

from thumbor.loaders import LoaderResult, file_loader_http_fallback as loader

from tests.base import TestCase


def dummy_load(context, path, callback, buffer=None, successful=True):
    callback(LoaderResult(buffer, successful))


class FileLoaderHttpFallbackFileTestCase(TestCase):

    @patch.object(loader.file_loader, 'load', partial(dummy_load, buffer='file'))
    def test_should_load_file(self):
        result = loader.load({}, 'image.jpg', lambda x: x).result()
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal('file')


class FileLoaderHttpFallbackHttpTestCase(TestCase):

    @patch.object(loader.file_loader, 'load', partial(dummy_load, successful=False))
    @patch.object(loader.http_loader, 'load', partial(dummy_load, buffer='http'))
    def test_should_load_http(self):
        url = 'http:/www.google.com/example_image.png'
        result = loader.load({}, url, self.stop).result()
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal('http')
