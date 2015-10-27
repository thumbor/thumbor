#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import abspath, join, dirname

from pyvows import Vows, expect
from tornado_pyvows.context import TornadoHTTPContext
import tornado.web

import thumbor.loaders.https_loader as loader
from thumbor.context import Context
from thumbor.config import Config
from thumbor.loaders import LoaderResult


fixture_for = lambda filename: abspath(join(dirname(__file__), 'fixtures', filename))


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('Hello')


class EchoUserAgentHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(self.request.headers['User-Agent'])


class HandlerMock(object):
    def __init__(self, headers):
        self.request = RequestMock(headers)


class RequestMock(object):
    def __init__(self, headers):
        self.headers = headers


class ResponseMock:
    def __init__(self, error=None, content_type=None, body=None, code=None):
        self.error = error
        self.code = code
        self.time_info = None

        self.headers = {
            'Content-Type': 'image/jpeg'
        }

        if content_type:
            self.headers['Content-Type'] = content_type

        self.body = body


@Vows.batch
class ReturnContentVows(Vows.Context):
    class ShouldReturnNoneOnError(Vows.Context):
        @Vows.async_topic
        def topic(self, callback):
            mock = ResponseMock(error='Error', code=599)
            ctx = Context(None, None, None)
            return loader.return_contents(mock, 'some-url', callback, ctx)

        def should_be_none(self, topic):
            result = topic.args[0]
            expect(result).to_be_instance_of(LoaderResult)
            expect(result.buffer).to_be_null()
            expect(result.successful).to_be_false()

    class ShouldReturnBodyIfValid(Vows.Context):
        @Vows.async_topic
        def topic(self, callback):
            mock = ResponseMock(body='body', code=200)
            ctx = Context(None, None, None)
            return loader.return_contents(mock, 'some-url', callback, ctx)

        def should_be_a_loader_result_with_hello(self, topic):
            result = topic.args[0]
            expect(result).to_be_instance_of(LoaderResult)
            expect(result.buffer).to_equal('body')
            expect(result.successful).to_be_true()


@Vows.batch
class HttpsLoader(TornadoHTTPContext):
    def get_app(self):
        application = tornado.web.Application([
            (r"/", MainHandler),
        ])

        return application

    class ValidateURL(TornadoHTTPContext):
        def topic(self):
            config = Config()
            config.ALLOWED_SOURCES = ['s.glbimg.com']
            ctx = Context(None, config, None)
            is_valid = loader.validate(ctx, 'http://www.google.com/logo.jpg')
            return is_valid

        def should_default_to_none(self, topic):
            expect(topic).to_be_false()

        class AllowAll(TornadoHTTPContext):
            def topic(self):
                config = Config()
                config.ALLOWED_SOURCES = []
                ctx = Context(None, config, None)
                is_valid = loader.validate(ctx, 'http://www.google.com/logo.jpg')
                return is_valid

            def should_validate(self, topic):
                expect(topic).to_be_true()

        class ValidDomainValidates(TornadoHTTPContext):
            def topic(self):
                config = Config()
                config.ALLOWED_SOURCES = ['s.glbimg.com']
                ctx = Context(None, config, None)
                is_valid = loader.validate(ctx, 'http://s.glbimg.com/logo.jpg')
                return is_valid

            def should_validate(self, topic):
                expect(topic).to_be_true()

        class UnallowedDomainDoesNotValidate(TornadoHTTPContext):
            def topic(self):
                config = Config()
                config.ALLOWED_SOURCES = ['s.glbimg.com']
                ctx = Context(None, config, None)
                is_valid = loader.validate(ctx, 'http://s2.glbimg.com/logo.jpg')
                return is_valid

            def should_validate(self, topic):
                expect(topic).to_be_false()

        class InvalidDomainDoesNotValidate(TornadoHTTPContext):
            def topic(self):
                config = Config()
                config.ALLOWED_SOURCES = ['s2.glbimg.com']
                ctx = Context(None, config, None)
                is_valid = loader.validate(ctx, '/glob=:sfoir%20%20%3Co-pmb%20%20%20%20_%20%20%20%200%20%20g.-%3E%3Ca%20hplass=')
                return is_valid

            def should_validate(self, topic):
                expect(topic).to_be_false()

    class NormalizeURL(TornadoHTTPContext):
        def topic(self):
            pass

        class WhenStartsWithHttp(TornadoHTTPContext):
            def topic(self):
                return loader._normalize_url('http://some.url')

            def should_return_same_url(self, topic):
                expect(topic).to_equal('http://some.url')

        class WhenStartsWithHttps(TornadoHTTPContext):
            def topic(self):
                return loader._normalize_url('https://some.url')

            def should_return_same_url(self, topic):
                expect(topic).to_equal('https://some.url')

        class WhenDoesNotStartWithHttp(TornadoHTTPContext):
            def topic(self):
                return loader._normalize_url('some.url')

            def should_return_normalized_url(self, topic):
                expect(topic).to_equal('https://some.url')
