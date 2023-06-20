#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

# Test file
# pylint: disable=protected-access

import re
import time
from os.path import abspath, dirname, join
from urllib.parse import quote

import tornado.web
from preggy import expect
from tornado.httpclient import AsyncHTTPClient
from tornado.testing import gen_test

import thumbor.loaders.http_loader as loader
from tests.base import TestCase
from thumbor.config import Config
from thumbor.context import Context
from thumbor.loaders import LoaderResult


def fixture_for(filename):
    return abspath(join(dirname(__file__), "fixtures", filename))


class MainHandler(tornado.web.RequestHandler):
    async def get(self):
        self.write("Hello")


class TimeoutHandler(tornado.web.RequestHandler):
    async def get(self):
        time.sleep(1.2)
        self.write("Hello")


class EchoUserAgentHandler(tornado.web.RequestHandler):
    async def get(self):
        self.write(self.request.headers["User-Agent"])


class EchoAllHeadersHandler(tornado.web.RequestHandler):
    async def get(self):
        for header, value in sorted(self.request.headers.items()):
            self.write(f"{header}:{value}\n")


class HandlerMock:
    def __init__(self, headers):
        self.request = RequestMock(headers)


class RequestMock:
    def __init__(self, headers):
        self.headers = headers


class ResponseMock:
    def __init__(self, error=None, content_type=None, body=None, code=None):
        self.error = error
        self.code = code
        self.time_info = None

        self.headers = {"Content-Type": "image/jpeg"}

        if content_type:
            self.headers["Content-Type"] = content_type

        self.body = body


class ReturnContentTestCase(TestCase):
    def test_return_none_on_error(self):
        response_mock = ResponseMock(error="Error", code=599)
        ctx = Context(None, None, None)
        result = loader.return_contents(response_mock, "some-url", ctx)
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_be_null()
        expect(result.successful).to_be_false()

    def test_return_body_if_valid(self):
        response_mock = ResponseMock(body="body", code=200)
        ctx = Context(None, None, None)
        result = loader.return_contents(response_mock, "some-url", ctx)
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal("body")

    def test_return_upstream_error_on_body_none(self):
        response_mock = ResponseMock(body=None, code=200)
        ctx = Context(None, None, None)
        result = loader.return_contents(response_mock, "some-url", ctx)
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_be_null()
        expect(result.successful).to_be_false()
        expect(result.error).to_equal(LoaderResult.ERROR_UPSTREAM)

    def test_return_upstream_error_on_body_empty(self):
        response_mock = ResponseMock(body="", code=200)
        ctx = Context(None, None, None)
        result = loader.return_contents(response_mock, "some-url", ctx)
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_be_null()
        expect(result.successful).to_be_false()
        expect(result.error).to_equal(LoaderResult.ERROR_UPSTREAM)


class ValidateUrlTestCase(TestCase):
    def test_with_allowed_sources(self):
        config = Config()
        config.ALLOWED_SOURCES = [
            "s.glbimg.com",
            re.compile(r"https://www\.google\.com/img/.*"),
        ]
        ctx = Context(None, config, None)
        expect(
            loader.validate(ctx, "http://www.google.com/logo.jpg")
        ).to_be_false()
        expect(
            loader.validate(ctx, "http://s2.glbimg.com/logo.jpg")
        ).to_be_false()
        expect(
            loader.validate(
                ctx,
                "/glob=:sfoir%20%20%3Co-pmb%20%20%20%20_%20%20%20%200%20%20g.-%3E%3Ca%20hplass=",  # NOQA, pylint: disable=line-too-long
            )
        ).to_be_false()
        expect(
            loader.validate(ctx, "https://www.google.com/img/logo.jpg")
        ).to_be_true()
        expect(
            loader.validate(ctx, "http://s.glbimg.com/logo.jpg")
        ).to_be_true()

    def test_without_allowed_sources(self):
        config = Config()
        config.ALLOWED_SOURCES = []
        ctx = Context(None, config, None)
        is_valid = loader.validate(ctx, "http://www.google.com/logo.jpg")
        expect(is_valid).to_be_true()


class NormalizeUrlTestCase(TestCase):
    def test_should_normalize_url(self):
        for url in ["http://some.url", "some.url"]:
            expect(loader._normalize_url(url)).to_equal("http://some.url")

    def test_should_normalize_quoted_url(self):
        url = (
            "https%3A//www.google.ca/images/branding/googlelogo/2x"
            "/googlelogo_color_272x92dp.png"
        )
        expected = (
            "https://www.google.ca/images/branding/googlelogo/2x"
            "/googlelogo_color_272x92dp.png"
        )
        result = loader._normalize_url(url)
        expect(result).to_equal(expected)


class DummyAsyncHttpClientTestCase(TestCase):
    # By default Tornado allows to create one (Async)HttpClient per
    # IOLoop instance
    # http://www.tornadoweb.org/en/stable/httpclient.html#tornado.httpclient.AsyncHTTPClient
    # AsyncHTTPTestCase provides a lot of useful code, which starts http
    # server listening with an app running.
    # But it also constructs AsyncHttpClient, which then by default is
    # getting reused upon next calls to get new AsyncHttpClient. Some
    # test cases are requiring curl client to be initialized
    # (see http_loader.py) but, by the time http_loader configures
    # Tornado's AsyncHTTPClient, it's already too late,
    # since Tornado has http client initialized for given IOLoop.
    # Forcing new instance here, on test start up time, is ensuring
    # that it won't be treated as singleton and rather be disposable instance.
    def get_http_client(self):
        return AsyncHTTPClient(force_instance=True)

    def tearDown(self):
        AsyncHTTPClient().close()  # clean up singleton instance
        super().tearDown()


class HttpLoaderTestCase(DummyAsyncHttpClientTestCase):
    def get_app(self):
        application = tornado.web.Application([(r"/", MainHandler)])

        return application

    @gen_test
    async def test_load_with_callback(self):
        url = self.get_url("/")
        config = Config()
        ctx = Context(None, config, None)

        result = await loader.load(ctx, url)
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal("Hello")
        expect(result.successful).to_be_true()

    @gen_test
    async def test_load_not_found(self):
        url = self.get_url("/not-found.jpg")
        config = Config()
        config.HTTP_LOADER_CURL_ASYNC_HTTP_CLIENT = False
        ctx = Context(None, config, None)

        result = await loader.load(ctx, url)
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_be_null()
        expect(result.successful).to_be_false()
        expect(result.error).to_equal(LoaderResult.ERROR_NOT_FOUND)

    @gen_test
    async def test_load_with_utf8_url(self):
        url = self.get_url(quote("/maracujá.jpg".encode("utf-8")))
        config = Config()
        ctx = Context(None, config, None)

        with expect.error_not_to_happen(UnicodeDecodeError):
            await loader.load(ctx, url)

    @gen_test
    async def test_load_with_curl(self):
        url = self.get_url("/")
        config = Config()
        config.HTTP_LOADER_CURL_ASYNC_HTTP_CLIENT = True
        ctx = Context(None, config, None)

        result = await loader.load(ctx, url)
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal("Hello")
        expect(result.successful).to_be_true()


class HttpLoaderWithHeadersForwardingTestCase(DummyAsyncHttpClientTestCase):
    def get_app(self):
        application = tornado.web.Application([(r"/", EchoAllHeadersHandler)])

        return application

    @gen_test
    async def test_load_with_some_headers(self):
        url = self.get_url("/")
        config = Config()
        config.HTTP_LOADER_FORWARD_HEADERS_WHITELIST = ["X-Server"]
        handler_mock_options = {
            "Accept-Encoding": "gzip",
            "User-Agent": "Thumbor",
            "Host": "localhost",
            "Accept": "*/*",
            "X-Server": "thumbor",
        }
        ctx = Context(None, config, None, HandlerMock(handler_mock_options))

        result = await loader.load(ctx, url)
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer.decode()).to_include("X-Server:thumbor")

    @gen_test
    async def test_load_with_some_excluded_headers(self):
        url = self.get_url("/")
        config = Config()
        handler_mock_options = {
            "Accept-Encoding": "gzip",
            "User-Agent": "Thumbor",
            "Host": "localhost",
            "Accept": "*/*",
            "X-Server": "thumbor",
        }
        ctx = Context(None, config, None, HandlerMock(handler_mock_options))

        result = await loader.load(ctx, url)
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer.decode()).Not.to_include("X-Server:thumbor")

    @gen_test
    async def test_load_with_all_headers(self):
        url = self.get_url("/")
        config = Config()
        config.HTTP_LOADER_FORWARD_ALL_HEADERS = True
        handler_mock_options = {
            "X-Test": "123",
            "DNT": "1",
            "X-Server": "thumbor",
        }
        ctx = Context(None, config, None, HandlerMock(handler_mock_options))

        result = await loader.load(ctx, url)
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer.decode()).to_include("Dnt:1\n")
        expect(result.buffer.decode()).to_include("X-Server:thumbor\n")
        expect(result.buffer.decode()).to_include("X-Test:123\n")

    @gen_test
    async def test_load_with_empty_accept(self):
        url = self.get_url("/")
        config = Config()
        handler_mock_options = {
            "Accept-Encoding": "gzip",
            "User-Agent": "Thumbor",
            "Host": "localhost",
            "Accept": "",
            "X-Server": "thumbor",
        }
        ctx = Context(None, config, None, HandlerMock(handler_mock_options))

        result = await loader.load(ctx, url)
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer.decode()).to_include(
            "Accept:image/*;q=0.9,*/*;q=0.1\n"
        )


class HttpLoaderWithUserAgentForwardingTestCase(DummyAsyncHttpClientTestCase):
    def get_app(self):
        application = tornado.web.Application([(r"/", EchoUserAgentHandler)])

        return application

    @gen_test
    async def test_load_with_user_agent(self):
        url = self.get_url("/")
        config = Config()
        config.HTTP_LOADER_FORWARD_USER_AGENT = True
        ctx = Context(
            None, config, None, HandlerMock({"User-Agent": "test-user-agent"})
        )

        result = await loader.load(ctx, url)
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal("test-user-agent")

    @gen_test
    async def test_load_with_default_user_agent(self):
        url = self.get_url("/")
        config = Config()
        config.HTTP_LOADER_FORWARD_USER_AGENT = True
        config.HTTP_LOADER_DEFAULT_USER_AGENT = "DEFAULT_USER_AGENT"
        ctx = Context(None, config, None, HandlerMock({}))

        result = await loader.load(ctx, url)
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal("DEFAULT_USER_AGENT")


class HttpCurlNotFoundLoaderTestCase(DummyAsyncHttpClientTestCase):
    def get_app(self):
        application = tornado.web.Application([(r"/", TimeoutHandler)])

        return application

    @gen_test
    async def test_load_not_found(self):
        url = self.get_url("/not-found.jpg")
        config = Config()
        config.HTTP_LOADER_CURL_ASYNC_HTTP_CLIENT = True
        config.HTTP_LOADER_REQUEST_TIMEOUT = 1
        ctx = Context(None, config, None)

        result = await loader.load(ctx, url)
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_be_null()
        expect(result.successful).to_be_false()
        expect(result.error).to_equal(LoaderResult.ERROR_NOT_FOUND)


class HttpCurlTimeoutLoaderTestCase(DummyAsyncHttpClientTestCase):
    def get_app(self):
        application = tornado.web.Application([(r"/", TimeoutHandler)])

        return application

    @gen_test
    async def test_load_with_timeout(self):
        url = self.get_url("/")
        config = Config()
        config.HTTP_LOADER_CURL_ASYNC_HTTP_CLIENT = True
        config.HTTP_LOADER_REQUEST_TIMEOUT = 1
        ctx = Context(None, config, None)

        result = await loader.load(ctx, url)
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_be_null()
        expect(result.successful).to_be_false()

    @gen_test
    async def test_load_with_speed_timeout(self):
        url = self.get_url("/")
        config = Config()
        config.HTTP_LOADER_CURL_ASYNC_HTTP_CLIENT = True
        config.HTTP_LOADER_CURL_LOW_SPEED_TIME = 1
        config.HTTP_LOADER_CURL_LOW_SPEED_LIMIT = 1000000000
        ctx = Context(None, config, None)

        result = await loader.load(ctx, url)
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_be_null()
        expect(result.successful).to_be_false()


class HttpTimeoutLoaderTestCase(DummyAsyncHttpClientTestCase):
    def get_app(self):
        application = tornado.web.Application([(r"/", TimeoutHandler)])

        return application

    @gen_test
    async def test_load_without_curl_but_speed_timeout(self):
        url = self.get_url("/")
        config = Config()
        config.HTTP_LOADER_CURL_LOW_SPEED_TIME = 1
        config.HTTP_LOADER_CURL_LOW_SPEED_LIMIT = 1000000000
        ctx = Context(None, config, None)

        result = await loader.load(ctx, url)
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal("Hello")
        expect(result.successful).to_be_true()
