# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from asyncio import to_thread
from os import makedirs
from os.path import abspath, dirname, join
from pathlib import Path
from tempfile import TemporaryDirectory

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
    async def test_should_fail_with_percent_encoded_traversal(self):
        # %2e%2e decodes to ".." — must be blocked even though the encoded
        # form passes a naive abspath/startswith check on the raw string.
        result = await self.load_file("%2e%2e/%2e%2e/etc/passwd")
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal(None)
        expect(result.successful).to_be_false()

    @gen_test
    async def test_should_fail_with_mixed_encoded_traversal(self):
        # Mix of literal ".." and percent-encoded ".." segments.
        result = await self.load_file("../%2e%2e/etc/passwd")
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal(None)
        expect(result.successful).to_be_false()

    @gen_test
    async def test_should_fail_when_decoded_path_escapes_to_sibling_prefix(
        self,
    ):
        with TemporaryDirectory() as directory:
            root = join(directory, "images")
            sibling = join(directory, "images-sibling")
            makedirs(root)
            makedirs(sibling)

            await to_thread(
                Path(sibling, "secret.txt").write_bytes,
                b"secret",
            )

            config = Config(FILE_LOADER_ROOT_PATH=root)
            ctx = Context(config=config)
            result = await load(ctx, "%2e%2e/images-sibling/secret.txt")

        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal(None)
        expect(result.successful).to_be_false()

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
