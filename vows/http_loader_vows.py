#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import abspath, join, dirname

from pyvows import Vows, expect
from tornado.concurrent import Future
from tornado_pyvows.context import TornadoHTTPContext
import tornado.web

import thumbor.loaders.http_loader as loader
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
class HttpLoader(TornadoHTTPContext):
    def get_app(self):
        application = tornado.web.Application([
            (r"/", MainHandler),
        ])

        return application

    class LoadAndVerifyImage(TornadoHTTPContext):
        def topic(self):
            pass

        class Load(TornadoHTTPContext):
            @Vows.async_topic
            def topic(self, callback):
                url = self.get_url('/')
                loader.http_client = self._http_client

                config = Config()
                config.ALLOWED_SOURCES = ['s.glbimg.com']
                ctx = Context(None, config, None)

                loader.load(ctx, url, callback)

            def should_equal_hello(self, topic):
                result = topic.args[0]
                expect(result).to_be_instance_of(LoaderResult)
                expect(result.buffer).to_equal('Hello')
                expect(result.successful).to_be_true()

        class LoaderWithoutCallback(TornadoHTTPContext):
            def topic(self):
                url = self.get_url('/')
                loader.http_client = self._http_client

                config = Config()
                config.ALLOWED_SOURCES = ['s.glbimg.com']
                ctx = Context(None, config, None)

                return loader.load, ctx, url

            def should_be_callable_and_return_a_future(self, topic):
                load, ctx, url = topic
                future = load(ctx, url)
                expect(isinstance(future, Future)).to_be_true()


@Vows.batch
class HttpLoaderWithUserAgentForwarding(TornadoHTTPContext):
    def get_app(self):
        application = tornado.web.Application([
            (r"/", EchoUserAgentHandler),
        ])

        return application

    class Load(TornadoHTTPContext):
        @Vows.async_topic
        def topic(self, callback):
            url = self.get_url('/')
            loader.http_client = self._http_client

            config = Config()
            config.HTTP_LOADER_FORWARD_USER_AGENT = True
            ctx = Context(None, config, None, HandlerMock({"User-Agent": "test-user-agent"}))

            loader.load(ctx, url, callback)

        def should_equal_hello(self, topic):
            result = topic.args[0]

            expect(result).to_be_instance_of(LoaderResult)
            expect(result.buffer).to_equal('test-user-agent')

    class LoadDefaultUserAgent(TornadoHTTPContext):
        @Vows.async_topic
        def topic(self, callback):
            url = self.get_url('/')
            loader.http_client = self._http_client

            config = Config()
            config.HTTP_LOADER_FORWARD_USER_AGENT = True
            config.HTTP_LOADER_DEFAULT_USER_AGENT = "DEFAULT_USER_AGENT"
            ctx = Context(None, config, None, HandlerMock({}))

            loader.load(ctx, url, callback)

        def should_equal_hello(self, topic):
            result = topic.args[0]

            expect(result).to_be_instance_of(LoaderResult)
            expect(result.buffer).to_equal('DEFAULT_USER_AGENT')
