#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from os.path import abspath, dirname, join
from unittest.mock import patch

from preggy import expect
from tornado.testing import gen_test

import thumbor
import thumbor.loaders.file_loader_http_fallback as loader
from tests.base import TestCase
from thumbor.config import Config
from thumbor.context import Context
from thumbor.loaders import LoaderResult

STORAGE_PATH = abspath(join(dirname(__file__), "../fixtures/images/"))


async def dummy_file_load(
    context, url, normalize_url_func=None
):  # pylint: disable=unused-argument
    result = LoaderResult(
        successful=True,
        buffer="file",
    )

    return result


async def dummy_http_load(
    context, url, normalize_url_func=None
):  # pylint: disable=unused-argument
    result = LoaderResult(
        successful=True,
        buffer="http",
    )

    return result


class FileLoaderHttpFallbackFileTestCase(TestCase):
    def setUp(self):
        super().setUp()
        config = Config(FILE_LOADER_ROOT_PATH=STORAGE_PATH)
        self.ctx = Context(config=config)

    @patch.object(thumbor.loaders.file_loader, "load", dummy_file_load)
    @gen_test
    async def test_should_load_file(self):
        result = await loader.load(self.ctx, "image.jpg")
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal("file")


class FileLoaderHttpFallbackHttpTestCase(TestCase):
    @patch.object(thumbor.loaders.http_loader, "load", dummy_http_load)
    @gen_test
    async def test_should_load_http(self):
        url = self.get_url("http:/www.google.com/example_image.png")
        config = Config()
        ctx = Context(None, config, None)

        result = await loader.load(ctx, url)

        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal("http")

    @patch.object(thumbor.loaders.http_loader, "load", dummy_http_load)
    @gen_test
    async def test_should_fail_with_disallowed_origin(self):
        url = "http:/www.google.com/example_image.png"
        config = Config(ALLOWED_SOURCES=[".+.domain1.com"])
        ctx = Context(None, config, None)

        result = await loader.load(ctx, url)

        expect(result).to_be_instance_of(LoaderResult)
        expect(result.successful).to_be_false()
        expect(result.error).to_equal(LoaderResult.ERROR_BAD_REQUEST)
        expect(result.extras["reason"]).to_equal("Unallowed domain")
        expect(result.extras["source"]).to_equal(url)
