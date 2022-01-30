#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from unittest.mock import patch

import pytest
from preggy import expect
from tornado.testing import gen_test

from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.engines.pil import Engine
from thumbor.importer import Importer

# pylint: disable=broad-except,abstract-method,attribute-defined-outside-init,line-too-long,too-many-public-methods
# pylint: disable=too-many-lines


class EngineLoadException(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.FILTERS = []

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    @patch.object(Engine, "load", side_effect=ValueError)
    @gen_test
    async def test_should_error_on_engine_load_exception(self, _):
        response = await self.async_fetch("/unsafe/image.jpg")
        expect(response.code).to_equal(500)

    @pytest.mark.skip(
        reason="I disagree with this test. If the engine fails we "
        "should get an error, otherwise we may end up caching an invalid crop."
    )
    @gen_test
    async def test_should_release_ioloop_on_error_on_engine_exception(self):
        response = await self.async_fetch("/unsafe/fit-in/134x134/940x2.png")
        expect(response.code).to_equal(200)

    @pytest.mark.skip(
        reason="I disagree with this test. If the engine fails we "
        "should get an error, otherwise we may end up caching an invalid crop."
    )
    @gen_test
    async def test_should_exec_other_operations_on_error_on_engine_exception(
        self,
    ):  # NOQA
        response = await self.async_fetch(
            "/unsafe/fit-in/134x134/filters:equalize()/940x2.png"
        )
        expect(response.code).to_equal(200)

    @patch.object(Engine, "read", side_effect=Exception)
    @gen_test
    async def test_should_fail_with_500_upon_engine_read_exception(
        self, _
    ):  # NOQA
        response = await self.async_fetch("/unsafe/fit-in/134x134/940x2.png")
        expect(response.code).to_equal(500)
