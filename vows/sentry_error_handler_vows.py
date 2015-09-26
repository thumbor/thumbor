#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from thumbor import __version__
from thumbor.error_handlers.sentry import ErrorHandler
from thumbor.config import Config
from thumbor.context import Context, ServerParameters


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


@Vows.batch
class SentryErrorHandlerVows(Vows.Context):
    class WhenInvalidConfiguration(Vows.Context):
        @Vows.capture_error
        def topic(self):
            cfg = Config()
            ErrorHandler(cfg)

        def should_be_error(self, topic):
            expect(topic).to_be_an_error()
            expect(topic).to_be_an_error_like(RuntimeError)

    class WhenErrorOccurs(Vows.Context):
        def topic(self):
            cfg = Config(SECURITY_KEY='ACME-SEC', SENTRY_DSN_URL="http://sentry-dsn-url")
            server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
            server.security_key = 'ACME-SEC'
            ctx = Context(server, cfg, None)

            client_mock = FakeSentry("FAKE DSN")
            handler = ErrorHandler(cfg, client=client_mock)
            http_handler = FakeHandler()

            handler.handle_error(ctx, http_handler, RuntimeError("Test"))

            return client_mock

        def should_have_called_client(self, topic):
            expect(topic.captured_exceptions).not_to_be_empty()
            expect(topic.captured_exceptions).to_length(1)

            exception, args, kw = topic.captured_exceptions[0]
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
