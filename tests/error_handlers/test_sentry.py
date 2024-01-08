#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect
from sentry_sdk import Hub
from sentry_sdk.transport import Transport

from tests.base import TestCase
from thumbor import __version__
from thumbor.config import Config
from thumbor.context import ServerParameters
from thumbor.server import get_importer


class MockTransport(Transport):
    """
    Transport that stores events in memory instead of sending them to Sentry.
    """

    def __init__(self, options=None):
        super().__init__(options=options)
        self.captured_events = []

    def capture_event(self, event):
        self.captured_events.append(event)


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


class InvalidSentryTestCase(TestCase):
    def get_importer(self):
        return get_importer(self.config)

    def test_when_missing_dsn(self):
        self.config = Config(
            SECURITY_KEY="ACME-SEC",
            USE_CUSTOM_ERROR_HANDLING=True,
            ERROR_HANDLER_MODULE="thumbor.error_handlers.sentry",
        )
        with expect.error_to_happen(RuntimeError):
            self.get_importer()

    def test_when_invalid_path(self):
        self.config = Config(
            SECURITY_KEY="ACME-SEC",
            USE_CUSTOM_ERROR_HANDLING=True,
            SENTRY_DSN_URL="https://key@sentry.io/12345",
            ERROR_HANDLER_MODULE="thumbor.error_handlers.invalid",
        )
        with expect.error_to_happen(ImportError):
            self.get_importer()


class SentryTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.app = self.get_app()

        self.transport_mock = MockTransport()
        Hub.current.client.transport = self.transport_mock

        self.http_handler = FakeHandler()

    def get_server(self):
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return server

    def get_config(self):
        return Config(
            SECURITY_KEY="ACME-SEC",
            SENTRY_DSN_URL="https://key@sentry.io/12345",
            USE_CUSTOM_ERROR_HANDLING=True,
            ERROR_HANDLER_MODULE="thumbor.error_handlers.sentry",
            SENTRY_ENVIRONMENT="env",
        )

    def get_importer(self):
        return get_importer(self.config)

    def test_when_error_occurs_should_have_called_client(self):
        self.importer.error_handler.handle_error(
            self.context, self.http_handler, RuntimeError("Test")
        )

        expect(self.transport_mock.captured_events).not_to_be_empty()
        expect(self.transport_mock.captured_events).to_length(1)

        event = self.transport_mock.captured_events[0]

        expect(event["exception"]["values"][0]["type"]).to_equal(
            "RuntimeError"
        )

        expect(event["environment"]).to_equal("env")

        expect(event).to_include("extra")
        expect(event).to_include("request")
        request, extra = event["request"], event["extra"]

        expect(extra).to_include("thumbor-version")
        expect(extra["thumbor-version"]).to_equal(__version__)

        expect(extra).to_include("thumbor-loader")
        expect(extra["thumbor-loader"]).to_equal(self.config.LOADER)

        expect(extra).to_include("thumbor-storage")
        expect(extra["thumbor-storage"]).to_equal(self.config.STORAGE)

        expect(request).to_include("headers")
        expect(request["headers"]).to_length(2)

        expect(request["headers"]).to_include("Cookie")
        expect(request["headers"]["Cookie"]).to_equal("[Filtered]")
        expect(request["headers"]["header1"]).to_equal("value1")

        expect(request["query_string"]).to_equal("a=1&b=2")

        expect(event["modules"]).not_to_be_empty()
