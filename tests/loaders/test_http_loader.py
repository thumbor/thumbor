#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import time
from os.path import abspath, join, dirname
from preggy import expect
import mock
# from tornado.concurrent import Future
import tornado.web
from tests.base import PythonTestCase, TestCase
from tornado.concurrent import Future
import re
from six.moves.urllib.parse import quote

import thumbor.loaders.http_loader as loader
from thumbor.context import Context
from thumbor.config import Config
from thumbor.loaders import LoaderResult


def fixture_for(filename):
    return abspath(join(dirname(__file__), 'fixtures', filename))


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('Hello')


class TimeoutHandler(tornado.web.RequestHandler):
    def get(self):
        time.sleep(1.2)
        self.write('Hello')


class EchoUserAgentHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(self.request.headers['User-Agent'])


class EchoAllHeadersHandler(tornado.web.RequestHandler):
    def get(self):
        for header, value in sorted(self.request.headers.iteritems()):
            self.write("%s:%s\n" % (header, value))


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


class ReturnContentTestCase(PythonTestCase):

    def test_return_none_on_error(self):
        response_mock = ResponseMock(error='Error', code=599)
        callback_mock = mock.Mock()
        ctx = Context(None, None, None)
        loader.return_contents(response_mock, 'some-url', callback_mock, ctx)
        result = callback_mock.call_args[0][0]
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_be_null()
        expect(result.successful).to_be_false()

    def test_return_body_if_valid(self):
        response_mock = ResponseMock(body='body', code=200)
        callback_mock = mock.Mock()
        ctx = Context(None, None, None)
        loader.return_contents(response_mock, 'some-url', callback_mock, ctx)
        result = callback_mock.call_args[0][0]
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal('body')

    def test_return_upstream_error_on_body_none(self):
        response_mock = ResponseMock(body=None, code=200)
        callback_mock = mock.Mock()
        ctx = Context(None, None, None)
        loader.return_contents(response_mock, 'some-url', callback_mock, ctx)
        result = callback_mock.call_args[0][0]
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_be_null()
        expect(result.successful).to_be_false()
        expect(result.error).to_equal(LoaderResult.ERROR_UPSTREAM)

    def test_return_upstream_error_on_body_empty(self):
        response_mock = ResponseMock(body='', code=200)
        callback_mock = mock.Mock()
        ctx = Context(None, None, None)
        loader.return_contents(response_mock, 'some-url', callback_mock, ctx)
        result = callback_mock.call_args[0][0]
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_be_null()
        expect(result.successful).to_be_false()
        expect(result.error).to_equal(LoaderResult.ERROR_UPSTREAM)


class ValidateUrlTestCase(PythonTestCase):

    def test_with_allowed_sources(self):
        config = Config()
        config.ALLOWED_SOURCES = [
            's.glbimg.com',
            re.compile(r'https:\/\/www\.google\.com/img/.*')
        ]
        ctx = Context(None, config, None)
        expect(
            loader.validate(
                ctx,
                'http://www.google.com/logo.jpg'
            )
        ).to_be_false()
        expect(
            loader.validate(
                ctx,
                'http://s2.glbimg.com/logo.jpg'
            )
        ).to_be_false()
        expect(
            loader.validate(
                ctx,
                '/glob=:sfoir%20%20%3Co-pmb%20%20%20%20_%20%20%20%200%20%20g.-%3E%3Ca%20hplass='
            )
        ).to_be_false()
        expect(
            loader.validate(
                ctx,
                'https://www.google.com/img/logo.jpg'
            )
        ).to_be_true()
        expect(
            loader.validate(ctx, 'http://s.glbimg.com/logo.jpg')).to_be_true()

    def test_without_allowed_sources(self):
        config = Config()
        config.ALLOWED_SOURCES = []
        ctx = Context(None, config, None)
        is_valid = loader.validate(ctx, 'http://www.google.com/logo.jpg')
        expect(is_valid).to_be_true()


class NormalizeUrlTestCase(PythonTestCase):

    def test_should_normalize_url(self):
        for url in ['http://some.url', 'some.url']:
            expect(loader._normalize_url(url)).to_equal('http://some.url')

    def test_should_normalize_quoted_url(self):
        url = 'https%3A//www.google.ca/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png'
        expected = 'https://www.google.ca/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png'
        result = loader._normalize_url(url)
        expect(result).to_equal(expected)


class HttpLoaderTestCase(TestCase):

    def get_app(self):
        application = tornado.web.Application([
            (r"/", MainHandler),
        ])

        return application

    def setUp(self):
        super(HttpLoaderTestCase, self).setUp()
        # not sure how AsyncHTTPClient really works (see the
        # magic regarding quasi-singleton) but I need to
        # force the connection to be closed so that it can
        # be configured with the right http client implementation
        # afterwards, otherwise I will get a cached (and normally
        # wrong) implementation
        tornado.httpclient.AsyncHTTPClient().close()

    def test_load_with_callback(self):
        url = self.get_url('/')
        config = Config()
        ctx = Context(None, config, None)

        loader.load(ctx, url, self.stop)
        result = self.wait()
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal('Hello')
        expect(result.successful).to_be_true()

    def test_load_with_utf8_url(self):
        url = self.get_url(quote(u'/maracujá.jpg'.encode('utf-8')))
        config = Config()
        ctx = Context(None, config, None)

        with expect.error_not_to_happen(UnicodeDecodeError):
            loader.load(ctx, url, self.stop)
            self.wait()

    def test_load_with_curl(self):
        url = self.get_url('/')
        config = Config()
        config.HTTP_LOADER_CURL_ASYNC_HTTP_CLIENT = True
        ctx = Context(None, config, None)

        loader.load(ctx, url, self.stop)
        result = self.wait()
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal('Hello')
        expect(result.successful).to_be_true()

    def test_should_return_a_future(self):
        url = self.get_url('/')
        config = Config()
        ctx = Context(None, config, None)

        future = loader.load(ctx, url)
        expect(isinstance(future, Future)).to_be_true()


class HttpLoaderWithHeadersForwardingTestCase(TestCase):

    def get_app(self):
        application = tornado.web.Application([
            (r"/", EchoAllHeadersHandler),
        ])

        return application

    def test_load_with_some_headers(self):
        url = self.get_url('/')
        config = Config()
        config.HTTP_LOADER_FORWARD_HEADERS_WHITELIST = ["X-Server"]
        handler_mock_options = {
            "Accept-Encoding": "gzip",
            "User-Agent": "Thumbor",
            "Host": "localhost",
            "Accept": "*/*",
            "X-Server": "thumbor"
        }
        ctx = Context(None, config, None, HandlerMock(handler_mock_options))

        loader.load(ctx, url, self.stop)
        result = self.wait()
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_include("X-Server:thumbor")

    def test_load_with_some_excluded_headers(self):
        url = self.get_url('/')
        config = Config()
        handler_mock_options = {
            "Accept-Encoding": "gzip",
            "User-Agent": "Thumbor",
            "Host": "localhost",
            "Accept": "*/*",
            "X-Server": "thumbor"
        }
        ctx = Context(None, config, None, HandlerMock(handler_mock_options))

        loader.load(ctx, url, self.stop)
        result = self.wait()
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).Not.to_include("X-Server:thumbor")

    def test_load_with_all_headers(self):
        url = self.get_url('/')
        config = Config()
        config.HTTP_LOADER_FORWARD_ALL_HEADERS = True
        handler_mock_options = {"X-Test": "123", "DNT": "1", "X-Server": "thumbor"}
        ctx = Context(None, config, None, HandlerMock(handler_mock_options))

        loader.load(ctx, url, self.stop)
        result = self.wait()
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_include("Dnt:1\n")
        expect(result.buffer).to_include("X-Server:thumbor\n")
        expect(result.buffer).to_include("X-Test:123\n")


class HttpLoaderWithUserAgentForwardingTestCase(TestCase):

    def get_app(self):
        application = tornado.web.Application([
            (r"/", EchoUserAgentHandler),
        ])

        return application

    def test_load_with_user_agent(self):
        url = self.get_url('/')
        config = Config()
        config.HTTP_LOADER_FORWARD_USER_AGENT = True
        ctx = Context(None, config, None, HandlerMock({"User-Agent": "test-user-agent"}))

        loader.load(ctx, url, self.stop)
        result = self.wait()
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal('test-user-agent')

    def test_load_with_default_user_agent(self):
        url = self.get_url('/')
        config = Config()
        config.HTTP_LOADER_FORWARD_USER_AGENT = True
        config.HTTP_LOADER_DEFAULT_USER_AGENT = "DEFAULT_USER_AGENT"
        ctx = Context(None, config, None, HandlerMock({}))

        loader.load(ctx, url, self.stop)
        result = self.wait()
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal('DEFAULT_USER_AGENT')


class HttpCurlTimeoutLoaderTestCase(TestCase):

    def get_app(self):
        application = tornado.web.Application([
            (r"/", TimeoutHandler),
        ])

        return application

    def setUp(self):
        super(HttpCurlTimeoutLoaderTestCase, self).setUp()
        # not sure how AsyncHTTPClient really works (see the
        # magic regarding quasi-singleton) but I need to
        # force the connection to be closed so that it can
        # be configured with the right http client implementation
        # afterwards, otherwise I will get a cached (and normally
        # wrong) implementation
        tornado.httpclient.AsyncHTTPClient().close()

    def test_load_with_timeout(self):
        url = self.get_url('/')
        config = Config()
        config.HTTP_LOADER_CURL_ASYNC_HTTP_CLIENT = True
        config.HTTP_LOADER_REQUEST_TIMEOUT = 1
        ctx = Context(None, config, None)

        loader.load(ctx, url, self.stop)
        result = self.wait()
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_be_null()
        expect(result.successful).to_be_false()

    def test_load_with_speed_timeout(self):
        url = self.get_url('/')
        config = Config()
        config.HTTP_LOADER_CURL_ASYNC_HTTP_CLIENT = True
        config.HTTP_LOADER_CURL_LOW_SPEED_TIME = 1
        config.HTTP_LOADER_CURL_LOW_SPEED_LIMIT = 1000000000000
        ctx = Context(None, config, None)

        loader.load(ctx, url, self.stop)
        result = self.wait()
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_be_null()
        expect(result.successful).to_be_false()


class HttpTimeoutLoaderTestCase(TestCase):

    def get_app(self):
        application = tornado.web.Application([
            (r"/", TimeoutHandler),
        ])

        return application

    def setUp(self):
        super(HttpTimeoutLoaderTestCase, self).setUp()
        # not sure how AsyncHTTPClient really works (see the
        # magic regarding quasi-singleton) but I need to
        # force the connection to be closed so that it can
        # be configured with the right http client implementation
        # afterwards, otherwise I will get a cached (and normally
        # wrong) implementation
        tornado.httpclient.AsyncHTTPClient().close()

    def test_load_without_curl_but_speed_timeout(self):
        url = self.get_url('/')
        config = Config()
        config.HTTP_LOADER_CURL_LOW_SPEED_TIME = 1
        config.HTTP_LOADER_CURL_LOW_SPEED_LIMIT = 1000000000000
        ctx = Context(None, config, None)

        loader.load(ctx, url, self.stop)
        result = self.wait()
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal('Hello')
        expect(result.successful).to_be_true()
