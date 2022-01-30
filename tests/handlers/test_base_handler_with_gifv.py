#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from shutil import which

import pytest
from preggy import expect
from tornado.testing import gen_test

from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.importer import Importer

# pylint: disable=broad-except,abstract-method,attribute-defined-outside-init,line-too-long,too-many-public-methods
# pylint: disable=too-many-lines


class ImageOperationsWithGifVTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.FFMPEG_PATH = which("ffmpeg")
        cfg.OPTIMIZERS = [
            "thumbor.optimizers.gifv",
        ]

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        ctx = Context(server, cfg, importer)
        ctx.server.gifsicle_path = which("gifsicle")

        return ctx

    @gen_test
    async def test_should_convert_animated_gif_to_mp4_when_filter_without_params(  # NOQA
        self,
    ):
        response = await self.async_fetch(
            "/unsafe/filters:gifv()/animated.gif"
        )

        expect(response.code).to_equal(200)
        expect(response.headers["Content-Type"]).to_equal("video/mp4")

    @pytest.mark.skip(
        reason="This test is flaky due to some issue with webM and Ubuntu. Need to look"
        " into it later"
    )
    @gen_test
    async def test_should_convert_animated_gif_to_webm_when_filter_with_gifv_webm_param(  # NOQA
        self,
    ):
        response = await self.async_fetch(
            "/unsafe/filters:gifv(webm)/animated.gif"
        )

        expect(response.code).to_equal(200)
        expect(response.headers["Content-Type"]).to_equal("video/webm")

    @gen_test
    async def test_should_convert_animated_gif_to_mp4_with_filter_without_params(  # NOQA
        self,
    ):
        response = await self.async_fetch(
            "/unsafe/filters:gifv(mp4):background_color(ff00ff)/animated.gif"
        )

        expect(response.code).to_equal(200)
        expect(response.headers["Content-Type"]).to_equal("video/mp4")
