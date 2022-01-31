#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from os.path import abspath, dirname, join

from preggy import expect
from tornado.testing import gen_test

from tests.base import TestCase
from thumbor.compatibility.storage import Storage
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.importer import Importer

STORAGE_PATH = abspath(join(dirname(__file__), "../fixtures/images/"))


class CompatibilityStorageTestCase(TestCase):
    def get_image_path(self, name):
        return f"./tests/fixtures/images/{name}"

    def get_image_bytes(self, name):
        with open(self.get_image_path(name), "rb") as img:
            return img.read()

    def get_image_url(self, name):
        return f"s.glbimg.com/some/{name}"

    def get_context(self):
        config = Config(
            FILE_LOADER_ROOT_PATH=STORAGE_PATH,
            COMPATIBILITY_LEGACY_STORAGE="tests.compatibility.legacy_file_storage",
            STORES_CRYPTO_KEY_FOR_EACH_IMAGE=True,
        )
        importer = Importer(config)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return Context(server, config=config, importer=importer)

    @gen_test
    async def test_should_raise_for_invalid_compatibility_storage(self):
        config = Config(
            FILE_LOADER_ROOT_PATH=STORAGE_PATH,
            STORES_CRYPTO_KEY_FOR_EACH_IMAGE=True,
        )
        importer = Importer(config)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        ctx = Context(server, config=config, importer=importer)
        storage = Storage(ctx)

        with expect.error_to_happen(
            RuntimeError,
            message=(
                "The 'COMPATIBILITY_LEGACY_STORAGE' configuration should "
                "point to a valid storage when using compatibility storage."
            ),
        ):
            await storage.get("invalid-path")

    @gen_test
    async def test_should_return_none_for_invalid_image(self):
        storage = Storage(self.context)

        result = await storage.get("invalid-path")

        expect(result).to_be_null()

    @gen_test
    async def test_should_get(self):
        url = self.get_image_url("image.jpg")
        image_bytes = self.get_image_bytes("image.jpg")
        storage = Storage(self.context)
        await storage.put(url, image_bytes)

        result = await storage.get(url)

        expect(result).not_to_be_null()
        expect(result).not_to_be_an_error()
        expect(result).to_equal(image_bytes)

    @gen_test
    async def test_should_put(self):
        url = self.get_image_url("image.jpg")
        image_bytes = self.get_image_bytes("image.jpg")
        storage = Storage(self.context)

        await storage.put(url, image_bytes)

        result = await storage.get(url)
        expect(result).not_to_be_null()
        expect(result).not_to_be_an_error()
        expect(result).to_equal(image_bytes)

    @gen_test
    async def test_should_put_detector_data(self):
        iurl = self.get_image_url("image_7.jpg")
        ibytes = self.get_image_bytes("image.jpg")
        storage = Storage(self.context)
        await storage.put(iurl, ibytes)

        await storage.put_detector_data(iurl, "some-data")

        got = await storage.get_detector_data(iurl)
        expect(got).not_to_be_null()
        expect(got).not_to_be_an_error()
        expect(got).to_equal("some-data")

    @gen_test
    async def test_should_put_crypto(self):
        iurl = self.get_image_url("image_7.jpg")
        ibytes = self.get_image_bytes("image.jpg")
        storage = Storage(self.context)
        await storage.put(iurl, ibytes)

        await storage.put_crypto(iurl)

        got = await storage.get_crypto(iurl)
        expect(got).not_to_be_null()
        expect(got).not_to_be_an_error()
        expect(got).to_equal("ACME-SEC")

    @gen_test
    async def test_exists(self):
        iurl = self.get_image_url("image_7.jpg")
        ibytes = self.get_image_bytes("image.jpg")
        storage = Storage(self.context)
        await storage.put(iurl, ibytes)

        exists = await storage.exists(iurl)
        not_exists = await storage.exists("some-invalid-random-file.jpg")

        expect(exists).to_be_true()
        expect(not_exists).to_be_false()

    @gen_test
    async def test_remove(self):
        iurl = self.get_image_url("image_7.jpg")
        ibytes = self.get_image_bytes("image.jpg")
        storage = Storage(self.context)
        await storage.put(iurl, ibytes)
        exists = await storage.exists(iurl)
        expect(exists).to_be_true()

        await storage.remove(iurl)

        not_exists = await storage.exists(iurl)
        expect(not_exists).to_be_false()
