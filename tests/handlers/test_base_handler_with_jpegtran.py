#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import os
import subprocess
import tempfile
from shutil import which

import pytest
from preggy import expect
from tornado.testing import gen_test

from tests.handlers.test_base_handler import (
    EXIFTOOL_AVAILABLE,
    JPEGTRAN_AVAILABLE,
    BaseImagingTestCase,
)
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.importer import Importer

# pylint: disable=broad-except,abstract-method,attribute-defined-outside-init,line-too-long,too-many-public-methods
# pylint: disable=too-many-lines


@pytest.mark.skipif(
    not JPEGTRAN_AVAILABLE or not EXIFTOOL_AVAILABLE,
    reason="In order to run thumbor's tests please install both jpegtran and exiftool",
)
class ImageOperationsWithJpegtranTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.JPEGTRAN_PATH = which("jpegtran")
        cfg.PROGRESSIVE_JPEG = (True,)
        cfg.RESULT_STORAGE_STORES_UNSAFE = (True,)
        cfg.OPTIMIZERS = [
            "thumbor.optimizers.jpegtran",
        ]

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        ctx = Context(server, cfg, importer)
        return ctx

    @gen_test
    async def test_should_optimize_jpeg(self):
        response = await self.async_fetch("/unsafe/200x200/image.jpg")

        tmp_fd, tmp_file_path = tempfile.mkstemp(suffix=".jpg")
        fixture = os.fdopen(tmp_fd, "wb")
        fixture.write(response.body)
        fixture.close()

        exiftool = which("exiftool")
        if not exiftool:
            raise AssertionError(
                "exiftool was not found. Please install it to run thumbor's tests."
            )

        command = [exiftool, tmp_file_path, "-DeviceModel", "-EncodingProcess"]

        try:
            output = subprocess.check_output(command, stdin=subprocess.DEVNULL)

            expect(response.code).to_equal(200)
            expect(output).to_equal(
                "Encoding Process                : Progressive DCT, Huffman coding\n"
            )
        finally:
            os.remove(tmp_file_path)

    @gen_test
    async def test_with_meta(self):
        response = await self.async_fetch("/unsafe/meta/800x400/image.jpg")
        expect(response.code).to_equal(200)

    @gen_test
    async def test_with_meta_cached(self):
        await self.async_fetch("/unsafe/meta/800x400/image.jpg")
        response = await self.async_fetch("/unsafe/meta/800x400/image.jpg")
        expect(response.code).to_equal(200)
