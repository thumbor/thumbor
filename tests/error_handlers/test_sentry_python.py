#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect
from sentry_sdk import Hub

from thumbor import __version__
from thumbor.context import ServerParameters
from thumbor.config import Config
from thumbor.server import get_importer

from tests.base import TestCase
from sentry_sdk.transport import Transport


class MockTransport(Transport):
    """Baseclass for all transports.

    A transport is used to send an event to sentry.
    """

    def __init__(self, options=None):
        super(MockTransport, self).__init__(options=options)
        self.captured_events = []

    def capture_event(self, event):
        self.captured_events.append(event)


class FakeSentry(object):
    def __init__(self, dsn):
        self.captured_exceptions = []

    def captureException(self, exception, *args, **kw):
        self.captured_exceptions.append((exception, args, kw))


class FakeRequest(object):
    def __init__(self):
        self.headers = {
            'header1': 'value1',
            'Cookie': 'cookie1=value; cookie2=value2;'
        }

        self.url = "test/"
        self.method = "GET"
        self.arguments = []
        self.body = "body"
        self.query = "a=1&b=2"
        self.remote_ip = "127.0.0.1"

    def full_url(self):
        return "http://test/%s" % self.url


class FakeHandler(object):
    def __init__(self):
        self.request = FakeRequest()


class InvalidSentryTestCase(TestCase):
    def test_when_invalid_configuration(self):
        with expect.error_to_happen(RuntimeError):
            get_importer(self.get_config())

    def get_config(self):
        return Config(
            SECURITY_KEY='ACME-SEC',
            USE_CUSTOM_ERROR_HANDLING=True,
            ERROR_HANDLER_MODULE='thumbor.error_handlers.sentry_python',
        )


class SentryTestCase(TestCase):
    def setUp(self, *args, **kwargs):
        super(SentryTestCase, self).setUp(*args, **kwargs)
        self.importer = get_importer(self.get_config())

        client = Hub.current.client
        self.transport_mock = MockTransport()
        client.transport = self.transport_mock

        self.http_handler = FakeHandler()

    def get_server(self):
        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        return server

    def get_config(self):
        return Config(
            SECURITY_KEY='ACME-SEC',
            SENTRY_DSN_URL='https://sentry-dsn-url@sentry.io/12345',
            USE_CUSTOM_ERROR_HANDLING=True,
            ERROR_HANDLER_MODULE='thumbor.error_handlers.sentry_python',
        )

    def test_when_error_occurs_should_have_called_client(self):
        self.importer.error_handler.handle_error(self.context, self.http_handler, RuntimeError("Test"))

        expect(self.transport_mock.captured_events).not_to_be_empty()
        expect(self.transport_mock.captured_events).to_length(1)

        event = self.transport_mock.captured_events[0]

        expect(event['exception']['values'][0]['type']).to_equal("RuntimeError")

        expect(event).to_include('extra')
        expect(event).to_include('request')
        request, extra = event['request'], event['extra']

        expect(extra).to_include('thumbor-version')
        expect(extra['thumbor-version']).to_equal("'%s'" % __version__)

        expect(request).to_include('headers')
        expect(request['headers']).to_length(2)

        expect(request['headers']).to_include('Cookie')
        expect(request['headers']['Cookie']).to_equal('cookie1=value; cookie2=value2;')
        expect(request['headers']['header1']).to_equal('value1')

        expect(request['query_string']).to_equal('a=1&b=2')

        expect(event['modules']).not_to_be_empty()
