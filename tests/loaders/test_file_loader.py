# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from os.path import abspath, dirname, join

from tornado.testing import gen_test

from tests.base import TestCase
from thumbor.config import Config
from thumbor.context import Context
from thumbor.loaders import LoaderResult
from thumbor.loaders.file_loader import load

STORAGE_PATH = abspath(join(dirname(__file__), "../fixtures/images/"))


class FileLoaderTestCase(TestCase):
    def setUp(self):
        super().setUp()
        config = Config(FILE_LOADER_ROOT_PATH=STORAGE_PATH)
        self.ctx = Context(config=config)

    async def load_file(self, file_name):
        return await load(self.ctx, file_name)

    @gen_test
    async def test_should_load_file(self):
        result = await self.load_file("image.jpg")
        assert isinstance(result, LoaderResult)
        with open(join(STORAGE_PATH, "image.jpg"), "rb") as img:
            assert result.buffer == img.read()
            assert result.successful

    @gen_test
    async def test_should_fail_when_inexistent_file(self):
        result = await self.load_file("image_NOT.jpg")
        assert isinstance(result, LoaderResult)
        assert result.buffer is None
        assert not result.successful

    @gen_test
    async def test_should_fail_when_outside_root_path(self):
        result = await self.load_file("../__init__.py")
        assert isinstance(result, LoaderResult)
        assert result.buffer is None
        assert not result.successful

    @gen_test
    async def test_should_load_file_with_spaces_in_name(self):
        result = await self.load_file("image .jpg")
        assert isinstance(result, LoaderResult)
        with open(join(STORAGE_PATH, "image.jpg"), "rb") as img:
            assert result.buffer == img.read()
            assert result.successful

    @gen_test
    async def test_should_load_file_with_spaces_encoded_in_name(self):
        result = await self.load_file("image2%20.jpg")
        assert isinstance(result, LoaderResult)
        with open(join(STORAGE_PATH, "image2%20.jpg"), "rb") as img:
            assert result.buffer == img.read()
            assert result.successful
