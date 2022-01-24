#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import logging
from shutil import which
from unittest import TestCase, mock

from preggy import expect

from thumbor.utils import CONTENT_TYPE, EXTENSION, deprecated, logger


class UtilsTestCase(TestCase):
    def setUp(self):
        self.handled = False
        super().setUp()

    @staticmethod
    def test_can_get_content_type():
        expect(CONTENT_TYPE.get(".jpg")).to_equal("image/jpeg")
        expect(CONTENT_TYPE.get(".jpeg")).to_equal("image/jpeg")
        expect(CONTENT_TYPE.get(".gif")).to_equal("image/gif")
        expect(CONTENT_TYPE.get(".png")).to_equal("image/png")
        expect(CONTENT_TYPE.get(".webp")).to_equal("image/webp")
        expect(CONTENT_TYPE.get(".mp4")).to_equal("video/mp4")
        expect(CONTENT_TYPE.get(".webm")).to_equal("video/webm")
        expect(CONTENT_TYPE.get(".svg")).to_equal("image/svg+xml")
        expect(CONTENT_TYPE.get(".tif")).to_equal("image/tiff")
        expect(CONTENT_TYPE.get(".tiff")).to_equal("image/tiff")

    @staticmethod
    def test_can_get_extension():
        expect(EXTENSION.get("image/jpeg")).to_equal(".jpg")
        expect(EXTENSION.get("image/gif")).to_equal(".gif")
        expect(EXTENSION.get("image/png")).to_equal(".png")
        expect(EXTENSION.get("image/webp")).to_equal(".webp")
        expect(EXTENSION.get("video/mp4")).to_equal(".mp4")
        expect(EXTENSION.get("video/webm")).to_equal(".webm")
        expect(EXTENSION.get("image/svg+xml")).to_equal(".svg")
        expect(EXTENSION.get("image/tiff")).to_equal(".tif")

    @staticmethod
    def test_can_get_logger():
        expect(logger.name).to_equal("thumbor")

    @staticmethod
    def test_deprecated_logs_msg():
        @deprecated("func2")
        def test_func():
            pass

        with mock.patch.object(logger, "warning") as mock_warn:
            test_func()
            mock_warn.assert_called_once_with(
                "Deprecated function %s%s", "test_func", "func2"
            )

    @staticmethod
    def test_can_which_by_path():
        result = which("/bin/ls")
        expect(result).to_include("/bin/ls")

        result = which("/tmp")
        expect(result).to_be_null()

    @staticmethod
    def test_can_which_by_env():
        result = which("ls")
        expect(result).to_include("/bin/ls")

        result = which("invalid-command")
        expect(result).to_be_null()

    @staticmethod
    def test_logger_should_be_instance_of_python_logger():
        expect(logger).to_be_instance_of(logging.Logger)

    @staticmethod
    def test_logger_should_not_be_null():
        expect(logger).not_to_be_null()

    @staticmethod
    def test_logger_should_not_be_an_error():
        expect(logger).not_to_be_an_error()
