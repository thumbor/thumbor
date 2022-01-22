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
from thumbor.compatibility import compatibility_get
from thumbor.config import Config
from thumbor.context import Context
from thumbor.importer import Importer
from thumbor.loaders import LoaderResult

STORAGE_PATH = abspath(join(dirname(__file__), "../fixtures/images/"))


class SimpleCompatibilityTestCase(TestCase):
    @gen_test
    async def test_can_get_result(self):
        Importer.deprecated_monkey_patch_tornado_return_future()
        from tests.compatibility.legacy_file_loader import (  # pylint: disable=import-outside-toplevel
            load,
        )

        config = Config(FILE_LOADER_ROOT_PATH=STORAGE_PATH)
        ctx = Context(config=config)
        result = await compatibility_get(ctx, "image.jpg", func=load)
        expect(result).to_be_instance_of(LoaderResult)
        with open(join(STORAGE_PATH, "image.jpg"), "rb") as img:
            expect(result.buffer).to_equal(img.read())
            expect(result.successful).to_be_true()
