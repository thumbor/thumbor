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
from thumbor.config import Config
from thumbor.context import Context
from thumbor.importer import Importer
from thumbor.loaders import LoaderResult

STORAGE_PATH = abspath(join(dirname(__file__), "../fixtures/images/"))


class CompatibilityLoaderTestCase(TestCase):
    def get_context(self):
        config = Config(
            FILE_LOADER_ROOT_PATH=STORAGE_PATH,
            COMPATIBILITY_LEGACY_LOADER="tests.compatibility.legacy_file_loader",
        )
        importer = Importer(config)
        importer.import_modules()
        return Context(config=config, importer=importer)

    async def load_file(self, context, file_name):
        Importer.deprecated_monkey_patch_tornado_return_future()
        from thumbor.compatibility.loader import (  # pylint: disable=import-outside-toplevel
            load,
        )

        return await load(context, file_name)

    @gen_test
    async def test_should_raise_for_invalid_compatibility_loader(self):
        config = Config(
            FILE_LOADER_ROOT_PATH=STORAGE_PATH,
        )
        importer = Importer(config)
        importer.import_modules()
        ctx = Context(config=config, importer=importer)

        with expect.error_to_happen(
            RuntimeError,
            message=(
                "The 'COMPATIBILITY_LEGACY_LOADER' configuration should point "
                "to a valid loader when using compatibility loader."
            ),
        ):
            await self.load_file(ctx, "image.jpg")

    @gen_test
    async def test_should_load_file(self):
        result = await self.load_file(self.context, "image.jpg")
        expect(result).to_be_instance_of(LoaderResult)
        with open(join(STORAGE_PATH, "image.jpg"), "rb") as img:
            expect(result.buffer).to_equal(img.read())
            expect(result.successful).to_be_true()
