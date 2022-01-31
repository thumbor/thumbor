#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import shutil
from datetime import datetime
from os.path import dirname, exists, join
from tempfile import mkdtemp
from unittest import mock

from preggy import expect
from tornado.testing import gen_test

from tests.base import TestCase
from thumbor.config import Config
from thumbor.context import ServerParameters
from thumbor.storages.file_storage import Storage as FileStorage


class BaseFileStorageTestCase(TestCase):
    def get_config(self):
        tmp = mkdtemp(suffix="thumbor-file-storage")
        return Config(FILE_STORAGE_ROOT_PATH=tmp)

    def get_server(self):
        server = ServerParameters(
            8888, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return server

    def get_image_path(self, name):
        return f"./tests/fixtures/images/{name}"

    def get_image_bytes(self, name):
        with open(self.get_image_path(name), "rb") as img:
            return img.read()

    def get_image_url(self, name):
        return f"s.glbimg.com/some/{name}"


class FileStorageTestCase(BaseFileStorageTestCase):
    @gen_test
    async def test_creates_root_path_if_none_found(self):
        storage = FileStorage(self.context)
        storage.ensure_dir(self.config.FILE_STORAGE_ROOT_PATH)
        expect(exists(self.config.FILE_STORAGE_ROOT_PATH)).to_be_true()

    @gen_test
    async def test_can_store_image_should_be_in_catalog(self):
        url = self.get_image_url("image.jpg")
        image_bytes = self.get_image_bytes("image.jpg")
        storage = FileStorage(self.context)
        await storage.put(url, image_bytes)
        got = await storage.get(url)
        expect(got).not_to_be_null()
        expect(got).not_to_be_an_error()

    @gen_test
    async def test_can_store_image_with_spaces(self):
        url = self.get_image_url("image .jpg")
        image_bytes = self.get_image_bytes("image .jpg")
        storage = FileStorage(self.context)
        await storage.put(url, image_bytes)
        got = await storage.get(url)
        expect(got).not_to_be_null()
        expect(got).not_to_be_an_error()
        expect(got).to_equal(image_bytes)

    @gen_test
    async def test_can_store_image_with_spaces_encoded(self):
        url = self.get_image_url("image%20.jpg")
        image_bytes = self.get_image_bytes("image .jpg")
        storage = FileStorage(self.context)
        await storage.put(url, image_bytes)
        got = await storage.get(url)
        expect(got).not_to_be_null()
        expect(got).not_to_be_an_error()
        expect(got).to_equal(image_bytes)

    @gen_test
    async def test_can_store_images_in_same_folder(self):
        iurl = self.get_image_url("image_999.jpg")
        other_iurl = iurl.replace("/some/", "/some_other/")
        root_path = join(
            self.config.FILE_STORAGE_ROOT_PATH, dirname(other_iurl)
        )
        if exists(root_path):
            shutil.rmtree(root_path)

        storage = FileStorage(self.context)
        ibytes = self.get_image_bytes("image.jpg")
        await storage.put(other_iurl.replace("999", "998"), ibytes)
        await storage.put(other_iurl, ibytes)

        got = await storage.get(other_iurl)
        expect(got).not_to_be_null()
        expect(got).not_to_be_an_error()

    @gen_test
    async def test_can_get_image(self):
        iurl = self.get_image_url("image_2.jpg")
        ibytes = self.get_image_bytes("image.jpg")
        storage = FileStorage(self.context)
        await storage.put(iurl, ibytes)
        got = await storage.get(iurl)
        expect(got).not_to_be_null()
        expect(got).not_to_be_an_error()
        expect(got).to_equal(ibytes)

    @gen_test
    async def test_does_not_store_if_config_says_not_to(self):
        iurl = self.get_image_url("image_5.jpg")
        ibytes = self.get_image_bytes("image.jpg")
        storage = FileStorage(self.context)
        await storage.put(iurl, ibytes)
        await storage.put_crypto(iurl)
        got = await storage.get_crypto(iurl)
        expect(got).to_be_null()

    @gen_test
    async def test_detector_can_store_detector_data(self):
        iurl = self.get_image_url("image_7.jpg")
        ibytes = self.get_image_bytes("image.jpg")
        storage = FileStorage(self.context)
        await storage.put(iurl, ibytes)
        await storage.put_detector_data(iurl, "some-data")
        got = await storage.get_detector_data(iurl)
        expect(got).not_to_be_null()
        expect(got).not_to_be_an_error()
        expect(got).to_equal("some-data")

    @gen_test
    async def test_detector_returns_none_if_no_detector_data(self):
        iurl = self.get_image_url("image_10000.jpg")
        storage = FileStorage(self.context)
        got = await storage.get_detector_data(iurl)
        expect(got).to_be_null()


class ExpiredFileStorageTestCase(BaseFileStorageTestCase):
    def get_config(self):
        return Config(
            FILE_STORAGE_ROOT_PATH="/tmp/thumbor/file_storage/",
            STORAGE_EXPIRATION_SECONDS=10,
        )

    @gen_test
    async def test_cannot_get_expired_1_day_old_image(self):
        iurl = self.get_image_url("image_2.jpg")
        ibytes = self.get_image_bytes("image.jpg")
        storage = FileStorage(self.context)
        await storage.put(iurl, ibytes)
        current_timestamp = (
            datetime.utcnow() - datetime(1970, 1, 1)
        ).total_seconds()
        new_mtime = current_timestamp - 60 * 60 * 24
        with mock.patch(
            "thumbor.storages.file_storage.getmtime", return_value=new_mtime
        ):
            got = await storage.get(iurl)
        expect(got).to_be_null()
        expect(got).not_to_be_an_error()


class ExpirationNoneFileStorageTestCase(BaseFileStorageTestCase):
    def get_config(self):
        return Config(
            FILE_STORAGE_ROOT_PATH="/tmp/thumbor/file_storage/",
            STORAGE_EXPIRATION_SECONDS=None,
        )

    @gen_test
    async def test_can_get_if_expire_set_to_none(self):
        iurl = self.get_image_url("image_2.jpg")
        ibytes = self.get_image_bytes("image.jpg")
        storage = FileStorage(self.context)
        await storage.put(iurl, ibytes)
        got = await storage.get(iurl)
        expect(got).not_to_be_null()
        expect(got).not_to_be_an_error()


class CryptoBadConfFileStorageTestCase(BaseFileStorageTestCase):
    def get_config(self):
        return Config(
            FILE_STORAGE_ROOT_PATH="/tmp/thumbor/file_storage/",
            STORES_CRYPTO_KEY_FOR_EACH_IMAGE=True,
        )

    def get_server(self):
        server = super().get_server()
        server.security_key = ""
        return server

    @gen_test
    async def test_should_be_an_error(self):
        iurl = self.get_image_url("image_3.jpg")
        ibytes = self.get_image_bytes("image.jpg")
        storage = FileStorage(self.context)
        await storage.put(iurl, ibytes)

        msg = "STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be True if no SECURITY_KEY specified"
        with expect.error_to_happen(
            RuntimeError,
            message=msg,
        ):
            await storage.put_crypto(iurl)


class CryptoFileStorageTestCase(BaseFileStorageTestCase):
    def get_config(self):
        return Config(
            FILE_STORAGE_ROOT_PATH="/tmp/thumbor/file_storage/",
            STORES_CRYPTO_KEY_FOR_EACH_IMAGE=True,
        )

    @gen_test
    async def test_getting_crypto_for_a_new_image_returns_none(self):
        iurl = self.get_image_url("image_9999.jpg")
        storage = FileStorage(self.context)
        got = await storage.get_crypto(iurl)
        expect(got).to_be_null()

    @gen_test
    async def test_can_store_crypto(self):
        iurl = self.get_image_url("image_6.jpg")
        ibytes = self.get_image_bytes("image.jpg")
        storage = FileStorage(self.context)
        await storage.put(iurl, ibytes)
        await storage.put_crypto(iurl)
        got = await storage.get_crypto(iurl)
        expect(got).not_to_be_null()
        expect(got).not_to_be_an_error()
        expect(got).to_equal("ACME-SEC")
