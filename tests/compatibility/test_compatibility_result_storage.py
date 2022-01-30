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
from thumbor.compatibility.result_storage import Storage
from thumbor.config import Config
from thumbor.context import Context, RequestParameters, ServerParameters
from thumbor.importer import Importer

STORAGE_PATH = abspath(join(dirname(__file__), "../fixtures/images/"))


class CompatibilityResultStorageTestCase(TestCase):
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
            COMPATIBILITY_LEGACY_RESULT_STORAGE="tests.compatibility.legacy_file_result_storage",
            STORES_CRYPTO_KEY_FOR_EACH_IMAGE=True,
        )
        self.importer = Importer(config)
        self.importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return Context(server, config=config, importer=self.importer)

    @gen_test
    async def test_should_raise_for_invalid_compatibility_storage(self):
        request = RequestParameters(
            url="/image.jpg",
        )
        config = Config(
            FILE_LOADER_ROOT_PATH=STORAGE_PATH,
            STORES_CRYPTO_KEY_FOR_EACH_IMAGE=True,
        )
        importer = Importer(config)
        importer.import_modules()
        image_bytes = self.get_image_bytes("image.jpg")
        ctx = Context(self.context.server, config, importer)
        ctx.request = request
        storage = Storage(ctx)

        with expect.error_to_happen(
            RuntimeError,
            message=(
                "The 'COMPATIBILITY_LEGACY_RESULT_STORAGE' configuration should point "
                "to a valid result storage when using compatibility result storage."
            ),
        ):
            await storage.get()

        with expect.error_to_happen(
            RuntimeError,
            message=(
                "The 'COMPATIBILITY_LEGACY_RESULT_STORAGE' configuration should point "
                "to a valid result storage when using compatibility result storage."
            ),
        ):
            await storage.put(image_bytes)

    @gen_test
    async def test_should_put_and_get(self):
        request = RequestParameters(
            url="/image.jpg",
        )
        image_bytes = self.get_image_bytes("image.jpg")
        ctx = Context(self.context.server, self.context.config, self.importer)
        ctx.request = request
        storage = Storage(ctx)

        await storage.put(image_bytes)

        result = await storage.get()
        expect(result).not_to_be_null()
        expect(result).not_to_be_an_error()
        expect(result.successful).to_be_true()
        expect(result.buffer).to_equal(image_bytes)
