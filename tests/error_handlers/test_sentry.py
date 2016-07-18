#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect

from thumbor import __version__
from thumbor.error_handlers.sentry import ErrorHandler
from thumbor.context import ServerParameters
from thumbor.config import Config

from tests.base import TestCase


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
            ErrorHandler(self.config)


class SentryTestCase(TestCase):
    def setUp(self, *args, **kwargs):
        super(SentryTestCase, self).setUp(*args, **kwargs)
        self.client_mock = FakeSentry("FAKE DSN")
        self.http_handler = FakeHandler()

    def get_server(self):
        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        return server

    def get_config(self):
        return Config(
            SECURITY_KEY='ACME-SEC',
            SENTRY_DSN_URL="http://sentry-dsn-url"
        )

    def test_when_error_occurs_should_have_called_client(self):
        handler = ErrorHandler(self.config, client=self.client_mock)
        handler.handle_error(self.context, self.http_handler, RuntimeError("Test"))

        expect(self.client_mock.captured_exceptions).not_to_be_empty()
        expect(self.client_mock.captured_exceptions).to_length(1)

        exception, args, kw = self.client_mock.captured_exceptions[0]
        expect(exception.__class__.__name__).to_equal("RuntimeError")
        expect(kw).to_include('data')
        expect(kw).to_include('extra')

        data, extra = kw['data'], kw['extra']

        expect(extra).to_include('thumbor-version')
        expect(extra['thumbor-version']).to_equal(__version__)

        expect(extra).to_include('Headers')
        expect(extra['Headers']).to_length(2)

        expect(extra['Headers']).to_include('Cookie')
        expect(extra['Headers']['Cookie']).to_length(2)

        expect(data['modules']).not_to_be_empty()

        del data['modules']

        expect(data).to_be_like({
            'sentry.interfaces.Http': {
                'url': "http://test/test/",
                'method': "GET",
                'data': [],
                'body': "body",
                'query_string': "a=1&b=2"
            },
            'sentry.interfaces.User': {
                'ip': "127.0.0.1",
            }
        })
