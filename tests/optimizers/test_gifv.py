#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from shutil import which
from unittest import TestCase

import mock

from thumbor.config import Config
from thumbor.context import Context, RequestParameters
from thumbor.optimizers.gifv import Optimizer
from thumbor.utils import EXTENSION


class GifvOptimizerTest(TestCase):
    def setUp(self):
        self.os_path_exists_patcher = mock.patch("thumbor.optimizers.gifv.exists")
        self.mock_os_path_exists = self.os_path_exists_patcher.start()

    def tearDown(self):
        self.os_path_exists_patcher.stop()

    def get_context(self):
        conf = Config()
        conf.STATSD_HOST = ""
        conf.FFMPEG_PATH = which("ffmpeg")
        ctx = Context(config=conf)
        ctx.request = RequestParameters()
        ctx.request.filters.append("gifv")

        return ctx

    def test_should_run_for_gif(self):
        optimizer = Optimizer(self.get_context())
        self.assertTrue(optimizer.should_run(".gif", ""))

    def test_should_not_run_for_not_gif(self):
        optimizer = Optimizer(self.get_context())
        for ext in EXTENSION.items():
            if ext != ".gif":
                self.assertFalse(optimizer.should_run(ext, ""))

    def test_should_not_run_if_binary_ffmpeg_path_does_not_exist(self):
        self.mock_os_path_exists.return_value = False

        optimizer = Optimizer(self.get_context())
        self.assertFalse(optimizer.should_run(".gif", ""))

    def test_should_parse_background_color_with_valid_value(self):
        optimizer = Optimizer(self.get_context())
        magenta_unicode_hex = u"#ff00ff"
        self.assertEqual(
            optimizer.normalize_color_to_hex("ff00ff"), magenta_unicode_hex
        )
        self.assertEqual(
            optimizer.normalize_color_to_hex("#ff00ff"), magenta_unicode_hex
        )
        self.assertEqual(optimizer.normalize_color_to_hex("f0f"), magenta_unicode_hex)
        self.assertEqual(optimizer.normalize_color_to_hex("#f0f"), magenta_unicode_hex)
        self.assertEqual(
            optimizer.normalize_color_to_hex("magenta"), magenta_unicode_hex
        )

    def test_should_not_parse_background_color_with_invalid_value(self):
        optimizer = Optimizer(self.get_context())
        self.assertEqual(optimizer.normalize_color_to_hex("asdfasdfasfd"), None)
