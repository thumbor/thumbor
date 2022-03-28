#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import tempfile
from datetime import datetime
from os.path import abspath, dirname, join
from unittest import mock

from preggy import expect
from tornado.testing import gen_test

from thumbor.config import Config
from thumbor.context import RequestParameters
from thumbor.result_storages import ResultStorageResult
from thumbor.result_storages.file_storage import Storage as FileStorage
from thumbor.testing import TestCase


class BaseFileStorageTestCase(TestCase):
    def __init__(self, *args, **kw):
        self.storage_path = None
        self.context = None
        self.file_storage = None
        super().__init__(*args, **kw)

    def get_config(self):
        config = super().get_config()
        self.storage_path = (
            tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        )
        config.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = self.storage_path.name
        return config

    def tearDown(self):
        super().tearDown()
        if self.storage_path is not None:
            self.storage_path.cleanup()

    @staticmethod
    def get_request():
        return RequestParameters()

    @staticmethod
    def get_fixture_path():
        return abspath(join(dirname(__file__), "../fixtures/result_storages"))

    def get_context(self):
        ctx = super().get_context()
        cfg = self.get_config()
        ctx.config = cfg
        ctx.request = self.get_request()
        self.context = ctx
        self.file_storage = FileStorage(self.context)
        return ctx

    @staticmethod
    def get_http_path():
        return "http://example.com/path/to/a.jpg"


class FileStorageTestCase(BaseFileStorageTestCase):
    @gen_test
    async def test_normalized_path(self):
        expect(self.file_storage).not_to_be_null()
        expect(
            self.file_storage.normalize_path(self.get_http_path())
        ).to_equal(
            f"{self.storage_path.name}/default/b6/be/"
            "a3e916129541a9e7146f69a15eb4d7c77c98"
        )


class WebPFileStorageTestCase(BaseFileStorageTestCase):
    def get_config(self):
        self.storage_path = (
            tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        )
        return Config(
            AUTO_WEBP=True,
            RESULT_STORAGE_FILE_STORAGE_ROOT_PATH=self.storage_path.name,
        )

    def tearDown(self):
        super().tearDown()
        self.storage_path.cleanup()

    def get_request(self):  # pylint: disable=arguments-differ
        return RequestParameters(accepts_webp=True)

    @gen_test
    async def test_normalized_path_with_auto_webp_path(self):
        expect(self.file_storage).not_to_be_null()
        expect(
            self.file_storage.normalize_path(self.get_http_path())
        ).to_equal(
            f"{self.storage_path.name}/auto_webp/b6/be/"
            "a3e916129541a9e7146f69a15eb4d7c77c98"
        )


class ResultStorageResultTestCase(BaseFileStorageTestCase):
    def get_config(self):
        return Config(
            RESULT_STORAGE_FILE_STORAGE_ROOT_PATH=self.get_fixture_path()
        )

    def get_request(self):  # pylint: disable=arguments-differ
        return RequestParameters(url="image.jpg")

    @gen_test
    async def test_can_get_image_from_storage(self):
        result = await self.file_storage.get()

        expect(result).to_be_instance_of(ResultStorageResult)
        expect(result.successful).to_equal(True)
        expect(len(result)).to_equal(5319)
        expect(len(result)).to_equal(result.metadata["ContentLength"])
        expect(result.last_modified).to_be_instance_of(datetime)


class ExpiredFileStorageTestCase(BaseFileStorageTestCase):
    def get_config(self):
        return Config(
            RESULT_STORAGE_FILE_STORAGE_ROOT_PATH=self.get_fixture_path(),
            RESULT_STORAGE_EXPIRATION_SECONDS=10,
        )

    def get_request(self):  # pylint: disable=arguments-differ
        return RequestParameters(url="image.jpg")

    @gen_test
    async def test_cannot_get_expired_1_day_old_image(self):
        current_timestamp = (
            datetime.utcnow() - datetime(1970, 1, 1)
        ).total_seconds()
        new_mtime = current_timestamp - 60 * 60 * 24
        with mock.patch(
            "thumbor.result_storages.file_storage.getmtime",
            return_value=new_mtime,
        ):
            result = await self.file_storage.get()
        expect(result).to_be_null()
