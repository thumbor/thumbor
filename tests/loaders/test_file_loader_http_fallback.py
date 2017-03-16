#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from functools import partial

import tornado

from mock import patch
from preggy import expect
from tornado import gen

from thumbor.loaders import LoaderResult, file_loader_http_fallback as loader

from tests.base import TestCase


@gen.coroutine
def dummy_load(context, path, buffer=None, successful=True):
    raise gen.Return(LoaderResult(buffer, successful))


class FileLoaderHttpFallbackFileTestCase(TestCase):

    @patch.object(loader.file_loader, 'load', partial(dummy_load, buffer='file'))
    @tornado.testing.gen_test
    def test_should_load_file(self):
        result = yield loader.load({}, 'image.jpg')
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal('file')


class FileLoaderHttpFallbackHttpTestCase(TestCase):

    @patch.object(loader.file_loader, 'load', partial(dummy_load, successful=False))
    @patch.object(loader.http_loader, 'load', partial(dummy_load, buffer='http'))
    @tornado.testing.gen_test
    def test_should_load_http(self):
        url = 'http:/www.google.com/example_image.png'
        result = yield loader.load({}, url)
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal('http')
