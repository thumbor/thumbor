#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import abspath, join, dirname

from pyvows import Vows, expect

from thumbor.context import Context
from thumbor.config import Config
from thumbor.loaders.file_loader import load
from thumbor.loaders import LoaderResult


STORAGE_PATH = abspath(join(dirname(__file__), 'fixtures/'))


@Vows.batch
class FileLoaderVows(Vows.Context):

    def topic(self):
        config = Config(FILE_LOADER_ROOT_PATH=STORAGE_PATH)
        return Context(config=config)

    class LoadsFromRootPath(Vows.Context):
        @Vows.async_topic
        def topic(self, callback, context):
            load(context, 'image.jpg', callback)

        def should_load_file(self, data):
            result = data.args[0]
            expect(result).to_be_instance_of(LoaderResult)
            expect(result.buffer).to_equal(open(join(STORAGE_PATH, 'image.jpg')).read())
            expect(result.successful).to_be_true()

    class DoesNotLoadInexistentFile(Vows.Context):
        @Vows.async_topic
        def topic(self, callback, context):
            load(context, 'image_NOT.jpg', callback)

        def should_load_file(self, data):
            result = data.args[0]
            expect(result).to_be_instance_of(LoaderResult)
            expect(result.buffer).to_equal(None)
            expect(result.successful).to_be_false()

    class DoesNotLoadFromOutsideRootPath(Vows.Context):
        @Vows.async_topic
        def topic(self, callback, context):
            load(context, '../file_loader_vows.py', callback)

        def should_load_file(self, data):
            result = data.args[0]
            expect(result).to_be_instance_of(LoaderResult)
            expect(result.buffer).to_equal(None)
            expect(result.successful).to_be_false()
