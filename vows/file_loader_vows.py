#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import abspath, join, dirname

from pyvows import Vows, expect

from thumbor.context import Context
from thumbor.config import Config
from thumbor.loaders.file_loader import load


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
            expect(data.args[0]).to_equal(open(join(STORAGE_PATH, 'image.jpg')).read())

    class DoesNotLoadInexistentFile(Vows.Context):
        @Vows.async_topic
        def topic(self, callback, context):
            load(context, 'image_NOT.jpg', callback)

        def should_load_file(self, data):
            expect(data.args[0]).to_equal(None)

    class DoesNotLoadFromOutsideRootPath(Vows.Context):
        @Vows.async_topic
        def topic(self, callback, context):
            load(context, '../file_loader_vows.py', callback)

        def should_load_file(self, data):
            expect(data.args[0]).to_equal(None)
