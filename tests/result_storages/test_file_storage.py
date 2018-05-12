#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from datetime import datetime
from os.path import abspath, join, dirname
import mock
import random

from preggy import expect

from thumbor.context import Context, RequestParameters
from thumbor.config import Config
from thumbor.result_storages import ResultStorageResult
from thumbor.result_storages.file_storage import Storage as FileStorage

from tests.base import TestCase


class BaseFileStorageTestCase(TestCase):
    def get_config(self):
        return Config(
            RESULT_STORAGE_FILE_STORAGE_ROOT_PATH="/tmp/thumbor/result_storages%s" % (random.choice(['', '/']))
        )

    def get_request(self):
        return RequestParameters()

    def get_fixture_path(self):
        return abspath(join(dirname(__file__), '../fixtures/result_storages'))

    def get_context(self):
        cfg = self.get_config()
        ctx = Context(None, cfg, None)
        ctx.request = self.get_request()
        self.context = ctx
        self.file_storage = FileStorage(self.context)
        return ctx

    def get_http_path(self):
        return 'http://example.com/path/to/a.jpg'


class FileStorageTestCase(BaseFileStorageTestCase):
    def test_normalized_path(self):
        expect(self.file_storage).not_to_be_null()
        expect(self.file_storage.normalize_path(self.get_http_path())).to_equal(
            '/tmp/thumbor/result_storages/v2/ht/tp/example.com/path/to/a.jpg'
        )


class WebPFileStorageTestCase(BaseFileStorageTestCase):
    def get_config(self):
        return Config(
            AUTO_WEBP=True,
            RESULT_STORAGE_FILE_STORAGE_ROOT_PATH="/tmp/thumbor/result_storages%s" % (random.choice(['', '/']))
        )

    def get_request(self):
        return RequestParameters(accepts_webp=True)

    def test_normalized_path_with_auto_webp_path(self):
        expect(self.file_storage).not_to_be_null()
        expect(self.file_storage.normalize_path(self.get_http_path())).to_equal(
            '/tmp/thumbor/result_storages/v2/webp/ht/tp/example.com/path/to/a.jpg'
        )


class ResultStorageResultTestCase(BaseFileStorageTestCase):
    def get_config(self):
        return Config(
            RESULT_STORAGE_FILE_STORAGE_ROOT_PATH=self.get_fixture_path()
        )

    def get_request(self):
        return RequestParameters(url='image.jpg')

    def test_can_get_image_from_storage(self):
        callback = mock.Mock()
        self.file_storage.get(callback=callback)

        expect(callback.called).to_equal(True)
        result = callback.call_args[0][0]
        expect(result).to_be_instance_of(ResultStorageResult)
        expect(result.successful).to_equal(True)
        expect(len(result)).to_equal(5319)
        expect(len(result)).to_equal(result.metadata['ContentLength'])
        expect(result.last_modified).to_be_instance_of(datetime)


class ExpiredFileStorageTestCase(BaseFileStorageTestCase):
    def get_config(self):
        return Config(
            RESULT_STORAGE_FILE_STORAGE_ROOT_PATH=self.get_fixture_path(),
            RESULT_STORAGE_EXPIRATION_SECONDS=10
        )

    def get_request(self):
        return RequestParameters(url='image.jpg')

    def test_cannot_get_expired_1_day_old_image(self):
        callback = mock.Mock()
        current_timestamp = (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()
        new_mtime = current_timestamp - 60 * 60 * 24
        with mock.patch(
                'thumbor.result_storages.file_storage.getmtime',
                return_value=new_mtime
        ):
            self.file_storage.get(callback=callback)
        result = callback.call_args[0][0]
        expect(result).to_be_null()
