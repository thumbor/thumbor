#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import abspath, join, dirname

from pyvows import Vows, expect
from tornado_pyvows.context import TornadoHTTPContext
import tornado.web

import thumbor.loaders.http_loader as loader
from thumbor.context import Context
from thumbor.config import Config

fixture_for = lambda filename: abspath(join(dirname(__file__), 'fixtures', filename))

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('Hello')

class ResponseMock:
    def __init__(self, error=None, content_type=None, body=None):
        self.error = error

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
            return loader.return_contents(callback, ResponseMock(error='Error'))

        def should_be_none(self, topic):
            expect(topic.args[0]).to_be_null()
 
    class ShouldReturnNoneOnInvalidContentType(Vows.Context):
        @Vows.async_topic
        def topic(self, callback):
            return loader.return_contents(callback, ResponseMock(content_type='application/json'))

        def should_be_none(self, topic):
            expect(topic.args[0]).to_be_null()

    class ShouldReturnBodyIfValid(Vows.Context):
        @Vows.async_topic
        def topic(self, callback):
            return loader.return_contents(callback, ResponseMock(body='body'))

        def should_be_none(self, topic):
            expect(topic.args[0]).to_equal('body')

@Vows.batch
class HttpLoader(TornadoHTTPContext):
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

    class NormalizeURL(TornadoHTTPContext):
        class WhenStartsWithHttp(TornadoHTTPContext):
            def topic(self):
                return loader._normalize_url('http://some.url')

            def should_return_same_url(self, topic):
                expect(topic).to_equal('http://some.url')

        class WhenDoesNotStartWithHttp(TornadoHTTPContext):
            def topic(self):
                return loader._normalize_url('some.url')

            def should_return_normalized_url(self, topic):
                expect(topic).to_equal('http://some.url')

    class LoadAndVerifyImage(TornadoHTTPContext):
        class Load(TornadoHTTPContext):
            @Vows.async_topic
            def topic(self, callback):
                url = self.get_url('/')
                loader.http_client = self._http_client
                loader.load(None, url, callback)

            def should_equal_hello(self, topic):
                expect(topic).to_equal('Hello')

