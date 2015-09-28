#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import random

from pyvows import Vows, expect

from thumbor.context import Context, RequestParameters
from thumbor.config import Config
from thumbor.result_storages.file_storage import Storage as FileStorage

TEST_HTTP_PATH = 'http://example.com/path/to/a.jpg'


@Vows.batch
class ResultStoragesFileStorageVows(Vows.Context):
    class NormalizedPathWithAutoWebpVow(Vows.Context):
        def topic(self):
            config = Config(
                AUTO_WEBP=True,
                RESULT_STORAGE_FILE_STORAGE_ROOT_PATH="/tmp/thumbor/result_storages%s" % (random.choice(['', '/'])))
            context = Context(config=config)
            context.request = RequestParameters(accepts_webp=True)
            return FileStorage(context)

        def check_http_path(self, topic):
            expect(topic).not_to_be_null()
            expect(topic.normalize_path(TEST_HTTP_PATH)).to_equal(
                '/tmp/thumbor/result_storages/v2/webp/ht/tp/example.com/path/to/a.jpg'
            )

    class NormalizedPathNoWebpVow(Vows.Context):
        def topic(self):
            config = Config(
                AUTO_WEBP=False,
                RESULT_STORAGE_FILE_STORAGE_ROOT_PATH="/tmp/thumbor/result_storages%s" % (random.choice(['', '/'])))
            context = Context(config=config)
            context.request = RequestParameters(accepts_webp=False)
            return FileStorage(context)

        def check_http_path(self, topic):
            expect(topic).not_to_be_null()
            expect(topic.normalize_path(TEST_HTTP_PATH)).to_equal(
                '/tmp/thumbor/result_storages/v2/ht/tp/example.com/path/to/a.jpg'
            )
