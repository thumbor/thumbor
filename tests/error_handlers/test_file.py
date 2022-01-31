#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import json
import tempfile

from preggy import expect

from tests.base import TestCase
from thumbor import __version__
from thumbor.config import Config
from thumbor.context import ServerParameters
from thumbor.error_handlers.file import ErrorHandler


class FakeRequest:
    def __init__(self):
        self.headers = {
            "header1": "value1",
            "Cookie": "cookie1=value; cookie2=value2;",
        }

        self.url = "test/"
        self.method = "GET"
        self.arguments = []
        self.body = "body"
        self.query = "a=1&b=2"
        self.remote_ip = "127.0.0.1"

    def full_url(self):
        return f"http://test/{self.url}"


class FakeHandler:
    def __init__(self):
        self.request = FakeRequest()


class InvalidFileErrorHandlerTestCase(TestCase):
    def test_when_invalid_empty_configuration(self):
        with expect.error_to_happen(RuntimeError):
            ErrorHandler(self.config)

    def test_when_invalid_configuration_of_filename_with_context_should_be_error(
        self,
    ):
        cfg = Config(
            ERROR_FILE_NAME_USE_CONTEXT="server..port",
            ERROR_FILE_LOGGER="toto",
        )
        with expect.error_to_happen(RuntimeError):
            ErrorHandler(cfg)


class BasicFileErrorHandlerTestCase(TestCase):
    def get_config(self):
        self.tmp = (
            tempfile.NamedTemporaryFile(  # pylint: disable=consider-using-with
                prefix="thumborTest."
            )
        )
        return Config(SECURITY_KEY="ACME-SEC", ERROR_FILE_LOGGER=self.tmp.name)

    def get_server(self):
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return server

    def test_when_error_occurs_should_have_called_client(self):
        handler = ErrorHandler(self.config)
        http_handler = FakeHandler()
        handler.handle_error(self.context, http_handler, RuntimeError("Test"))
        content = self.tmp.read()
        log = json.loads(content.decode("utf-8"))
        del log["extra"]["timestamp"]
        expect(log).to_be_like(
            {
                "Http": {
                    "url": "http://test/test/",
                    "method": "GET",
                    "data": [],
                    "body": "body",
                    "query_string": "a=1&b=2",
                },
                "interfaces.User": {"ip": "127.0.0.1"},
                "exception": "Test",
                "extra": {
                    "thumbor-version": __version__,
                    "Headers": {
                        "header1": "value1",
                        "Cookie": {"cookie1": "value", "cookie2": "value2"},
                    },
                },
            }
        )


class FileErrorHandlerTestCase(TestCase):
    PORT = 8890

    def get_config(self):
        self.tmp = (
            tempfile.NamedTemporaryFile(  # pylint: disable=consider-using-with
                prefix=f"thumborTest.{self.PORT}."
            )
        )
        return Config(
            SECURITY_KEY="ACME-SEC",
            ERROR_FILE_LOGGER=self.tmp.name.replace(
                f"thumborTest.{self.PORT}.", "thumborTest.%i."
            ),
            ERROR_FILE_NAME_USE_CONTEXT="server.port",
        )

    def get_server(self):
        server = ServerParameters(
            self.PORT, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return server

    def test_when_error_occurs_i_use_context_should_have_called_client(self):
        handler = ErrorHandler(self.config)
        http_handler = FakeHandler()
        handler.handle_error(self.context, http_handler, RuntimeError("Test"))
        content = self.tmp.read()

        # check against json version
        log = json.loads(content.decode("utf-8"))
        del log["extra"]["timestamp"]
        expect(log).to_be_like(
            {
                "Http": {
                    "url": "http://test/test/",
                    "method": "GET",
                    "data": [],
                    "body": "body",
                    "query_string": "a=1&b=2",
                },
                "interfaces.User": {"ip": "127.0.0.1"},
                "exception": "Test",
                "extra": {
                    "thumbor-version": __version__,
                    "Headers": {
                        "header1": "value1",
                        "Cookie": {"cookie1": "value", "cookie2": "value2"},
                    },
                },
            }
        )
