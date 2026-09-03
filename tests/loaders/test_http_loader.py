# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# https://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

# Test file
# pylint: disable=protected-access

import os
import re
import time
from os.path import abspath, dirname, join
from unittest import mock
from urllib.parse import quote

import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado.testing import gen_test

import thumbor.loaders.http_loader as loader
from tests.base import TestCase
from thumbor import loaders
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


class CurlMock:
    LOW_SPEED_LIMIT = "LOW_SPEED_LIMIT"
    LOW_SPEED_TIME = "LOW_SPEED_TIME"
    PROXY = "PROXY"

    def __init__(self):
        self.options = {}

    def setopt(self, option, value):
        self.options[option] = value


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
        assert isinstance(result, LoaderResult)
        assert result.buffer is None
        assert not result.successful

    def test_return_body_if_valid(self):
        response_mock = ResponseMock(body="body", code=200)
        ctx = Context(None, None, None)
        result = loader.return_contents(response_mock, "some-url", ctx)
        assert isinstance(result, LoaderResult)
        assert result.buffer == "body"

    def test_return_upstream_error_on_body_none(self):
        response_mock = ResponseMock(body=None, code=200)
        ctx = Context(None, None, None)
        result = loader.return_contents(response_mock, "some-url", ctx)
        assert isinstance(result, LoaderResult)
        assert result.buffer is None
        assert not result.successful
        assert result.error == LoaderResult.ERROR_UPSTREAM

    def test_return_upstream_error_on_body_empty(self):
        response_mock = ResponseMock(body="", code=200)
        ctx = Context(None, None, None)
        result = loader.return_contents(response_mock, "some-url", ctx)
        assert isinstance(result, LoaderResult)
        assert result.buffer is None
        assert not result.successful
        assert result.error == LoaderResult.ERROR_UPSTREAM


class ValidateUrlTestCase(TestCase):
    def test_with_allowed_sources(self):
        config = Config()
        config.ALLOWED_SOURCES = [
            "s.glbimg.com",
            re.compile(r"https://www\.google\.com/img/.*"),
        ]
        ctx = Context(None, config, None)
        assert not loader.validate(
            ctx, "http://www.google.com/logo.jpg"  # NOSONAR
        )
        assert not loader.validate(ctx, "https://s2.glbimg.com/logo.jpg")
        assert not loader.validate(  # pylint: disable=line-too-long
            ctx,
            "/glob=:sfoir%20%20%3Co-pmb%20%20%20%20_%20%20%20%200%20%20g.-%3E%3Ca%20hplass=",
        )
        assert loader.validate(ctx, "https://www.google.com/img/logo.jpg")
        assert loader.validate(ctx, "https://s.glbimg.com/logo.jpg")

    def test_dot_in_string_pattern_is_literal(self):
        """Dots in plain-string patterns must not act as regex wildcards.

        e.g. "s.glbimg.com" must not match "sXglbimgYcom".
        """
        config = Config()
        config.ALLOWED_SOURCES = ["s.glbimg.com"]
        ctx = Context(None, config, None)
        assert loader.validate(ctx, "https://s.glbimg.com/logo.jpg")
        assert not loader.validate(ctx, "https://sXglbimgYcom/logo.jpg")
        assert not loader.validate(ctx, "https://sAglbimg.com/logo.jpg")

    def test_legacy_regex_string_pattern_still_works(self):
        loaders.WARNED_LEGACY_ALLOWED_SOURCE_REGEXES.clear()
        config = Config()
        config.ALLOWED_SOURCES = [r".+\.glbimg\.com"]
        ctx = Context(None, config, None)
        assert loader.validate(ctx, "https://s.glbimg.com/logo.jpg")
        assert loader.validate(ctx, "https://media.glbimg.com/logo.jpg")
        assert not loader.validate(ctx, "https://sXglbimgYcom/logo.jpg")

    def test_legacy_regex_string_pattern_logs_warning_once(self):
        loaders.WARNED_LEGACY_ALLOWED_SOURCE_REGEXES.clear()
        config = Config()
        config.ALLOWED_SOURCES = [r".+\.glbimg\.com"]
        ctx = Context(None, config, None)

        with mock.patch.object(loaders.logger, "warning") as warning:
            loader.validate(ctx, "https://s.glbimg.com/logo.jpg")
            loader.validate(ctx, "https://media.glbimg.com/logo.jpg")

        assert warning.call_count == 1
        assert "ALLOWED_SOURCES regex strings" in warning.call_args[0][0]

    def test_allows_compiled_regex_pattern(self):
        """Compiled patterns should work as real regexes."""
        config = Config()
        config.ALLOWED_SOURCES = [
            re.compile(r"https?://cdn\d+\.example\.com/.*")
        ]
        ctx = Context(None, config, None)
        assert loader.validate(
            ctx, "http://cdn1.example.com/img.jpg"  # NOSONAR
        )
        assert loader.validate(ctx, "https://cdn99.example.com/img.jpg")
        assert not loader.validate(ctx, "https://cdnXX.example.com/img.jpg")

    def test_without_allowed_sources(self):
        config = Config()
        config.ALLOWED_SOURCES = []
        ctx = Context(None, config, None)
        is_valid = loader.validate(ctx, "https://www.google.com/logo.jpg")
        assert is_valid


class NormalizeUrlTestCase(TestCase):
    def test_should_normalize_url(self):
        for url in ["http://some.url", "some.url"]:  # NOSONAR
            assert loader._normalize_url(url) == "http://some.url"  # NOSONAR

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
        assert result == expected


class EnvironmentProxyTestCase(TestCase):
    def test_should_use_http_proxy_environment_variable(self):
        env = {"http_proxy": "http://proxy.example:3128"}
        with mock.patch.dict(os.environ, env, clear=True):
            proxy_url, has_environment_proxy = loader._get_environment_proxy(
                "http://images.example/image.jpg"  # NOSONAR
            )

        assert proxy_url == "http://proxy.example:3128"
        assert has_environment_proxy

    def test_should_use_https_proxy_environment_variable(self):
        env = {"https_proxy": "http://proxy.example:3128"}
        with mock.patch.dict(os.environ, env, clear=True):
            proxy_url, has_environment_proxy = loader._get_environment_proxy(
                "https://images.example/image.jpg"
            )

        assert proxy_url == "http://proxy.example:3128"
        assert has_environment_proxy

    def test_should_fallback_to_all_proxy_environment_variable(self):
        env = {"all_proxy": "http://proxy.example:3128"}
        with mock.patch.dict(os.environ, env, clear=True):
            proxy_url, has_environment_proxy = loader._get_environment_proxy(
                "https://images.example/image.jpg"
            )

        assert proxy_url == "http://proxy.example:3128"
        assert has_environment_proxy

    def test_should_respect_no_proxy_environment_variable(self):
        env = {
            "http_proxy": "http://proxy.example:3128",
            "no_proxy": "images.example:8888",
        }
        with mock.patch.dict(os.environ, env, clear=True):
            proxy_url, has_environment_proxy = loader._get_environment_proxy(
                "http://images.example:8888/image.jpg"  # NOSONAR
            )

        assert proxy_url is None
        assert has_environment_proxy

    def test_should_ignore_no_proxy_without_proxy_environment_variable(self):
        env = {"no_proxy": "images.example"}
        with mock.patch.dict(os.environ, env, clear=True):
            proxy_url, has_environment_proxy = loader._get_environment_proxy(
                "http://images.example/image.jpg"  # NOSONAR
            )

        assert proxy_url is None
        assert not has_environment_proxy


class PrepareCurlCallbackTestCase(TestCase):
    def test_should_return_none_without_curl_options(self):
        assert loader._get_prepare_curl_callback(Config()) is None

    def test_should_set_environment_proxy_url(self):
        callback = loader._get_prepare_curl_callback(
            Config(), "http://proxy.example:3128"
        )
        curl = CurlMock()

        callback(curl)

        assert curl.options[CurlMock.PROXY] == "http://proxy.example:3128"

    def test_should_set_proxy_and_low_speed_options(self):
        config = Config()
        config.HTTP_LOADER_CURL_LOW_SPEED_TIME = 1
        config.HTTP_LOADER_CURL_LOW_SPEED_LIMIT = 100
        callback = loader._get_prepare_curl_callback(
            config, "http://proxy.example:3128"
        )
        curl = CurlMock()

        callback(curl)

        assert curl.options[CurlMock.PROXY] == "http://proxy.example:3128"
        assert curl.options[CurlMock.LOW_SPEED_TIME] == 1
        assert curl.options[CurlMock.LOW_SPEED_LIMIT] == 100


class DummyAsyncHttpClientTestCase(TestCase):
    # By default Tornado allows to create one (Async)HttpClient per
    # IOLoop instance
    # https://www.tornadoweb.org/en/stable/httpclient.html#tornado.httpclient.AsyncHTTPClient
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
    async def test_load_should_configure_environment_proxy(self):
        config = Config()
        ctx = Context(None, config, None)
        client = mock.Mock()
        client.fetch = mock.AsyncMock(
            return_value=ResponseMock(body=b"Hello", code=200)
        )
        prepare_curl_callback = mock.Mock()
        return_contents = mock.Mock(return_value=mock.sentinel.result)
        env = {"http_proxy": "http://proxy.example:3128"}

        with (
            mock.patch.dict(os.environ, env, clear=True),
            mock.patch.object(
                loader,
                "_get_prepare_curl_callback",
                return_value=prepare_curl_callback,
            ) as get_prepare_curl_callback,
            mock.patch.object(
                tornado.httpclient,
                "AsyncHTTPClient",
                return_value=client,
            ) as async_http_client,
        ):
            result = await loader.load(
                ctx,
                "images.example/image.jpg",
                return_contents_fn=return_contents,
            )

        async_http_client.configure.assert_called_once_with(
            "tornado.curl_httpclient.CurlAsyncHTTPClient",
            max_clients=config.HTTP_LOADER_MAX_CLIENTS,
        )
        get_prepare_curl_callback.assert_called_once_with(
            config, "http://proxy.example:3128"
        )
        request = client.fetch.await_args.args[0]
        assert request.url == "http://images.example/image.jpg"  # NOSONAR
        assert request.prepare_curl_callback is prepare_curl_callback
        assert result is mock.sentinel.result

    @gen_test
    async def test_load_should_not_apply_proxy_for_no_proxy_target(self):
        config = Config()
        ctx = Context(None, config, None)
        client = mock.Mock()
        client.fetch = mock.AsyncMock(
            return_value=ResponseMock(body=b"Hello", code=200)
        )
        return_contents = mock.Mock(return_value=mock.sentinel.result)
        env = {
            "http_proxy": "http://proxy.example:3128",
            "no_proxy": "images.example",
        }

        with (
            mock.patch.dict(os.environ, env, clear=True),
            mock.patch.object(
                loader,
                "_get_prepare_curl_callback",
                wraps=loader._get_prepare_curl_callback,
            ) as get_prepare_curl_callback,
            mock.patch.object(
                tornado.httpclient,
                "AsyncHTTPClient",
                return_value=client,
            ) as async_http_client,
        ):
            result = await loader.load(
                ctx,
                "http://images.example/image.jpg",  # NOSONAR
                return_contents_fn=return_contents,
            )

        async_http_client.configure.assert_called_once_with(
            "tornado.curl_httpclient.CurlAsyncHTTPClient",
            max_clients=config.HTTP_LOADER_MAX_CLIENTS,
        )
        get_prepare_curl_callback.assert_called_once_with(config, None)
        request = client.fetch.await_args.args[0]
        assert request.prepare_curl_callback is None
        assert result is mock.sentinel.result

    @gen_test
    async def test_load_with_callback(self):
        url = self.get_url("/")
        config = Config()
        ctx = Context(None, config, None)

        result = await loader.load(ctx, url)
        assert isinstance(result, LoaderResult)
        assert result.buffer == b"Hello"
        assert result.successful

    @gen_test
    async def test_load_not_found(self):
        url = self.get_url("/not-found.jpg")
        config = Config()
        config.HTTP_LOADER_CURL_ASYNC_HTTP_CLIENT = False
        ctx = Context(None, config, None)

        result = await loader.load(ctx, url)
        assert isinstance(result, LoaderResult)
        assert result.buffer is None
        assert not result.successful
        assert result.error == LoaderResult.ERROR_NOT_FOUND

    @gen_test
    async def test_load_with_utf8_url(self):
        url = self.get_url(quote("/maracujá.jpg".encode("utf-8")))
        config = Config()
        ctx = Context(None, config, None)

        await loader.load(ctx, url)

    @gen_test
    async def test_load_with_curl(self):
        url = self.get_url("/")
        config = Config()
        config.HTTP_LOADER_CURL_ASYNC_HTTP_CLIENT = True
        ctx = Context(None, config, None)

        result = await loader.load(ctx, url)
        assert isinstance(result, LoaderResult)
        assert result.buffer == b"Hello"
        assert result.successful


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
        assert isinstance(result, LoaderResult)
        assert "X-Server:thumbor" in result.buffer.decode()

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
        assert isinstance(result, LoaderResult)
        assert "X-Server:thumbor" not in result.buffer.decode()

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
        assert isinstance(result, LoaderResult)
        assert "Dnt:1\n" in result.buffer.decode()
        assert "X-Server:thumbor\n" in result.buffer.decode()
        assert "X-Test:123\n" in result.buffer.decode()

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
        assert isinstance(result, LoaderResult)
        assert "Accept:image/*;q=0.9,*/*;q=0.1\n" in result.buffer.decode()


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
        assert isinstance(result, LoaderResult)
        assert result.buffer == b"test-user-agent"

    @gen_test
    async def test_load_with_default_user_agent(self):
        url = self.get_url("/")
        config = Config()
        config.HTTP_LOADER_FORWARD_USER_AGENT = True
        config.HTTP_LOADER_DEFAULT_USER_AGENT = "DEFAULT_USER_AGENT"
        ctx = Context(None, config, None, HandlerMock({}))

        result = await loader.load(ctx, url)
        assert isinstance(result, LoaderResult)
        assert result.buffer == b"DEFAULT_USER_AGENT"


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
        assert isinstance(result, LoaderResult)
        assert result.buffer is None
        assert not result.successful
        assert result.error == LoaderResult.ERROR_NOT_FOUND


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
        assert isinstance(result, LoaderResult)
        assert result.buffer is None
        assert not result.successful

    @gen_test
    async def test_load_with_speed_timeout(self):
        url = self.get_url("/")
        config = Config()
        config.HTTP_LOADER_CURL_ASYNC_HTTP_CLIENT = True
        config.HTTP_LOADER_CURL_LOW_SPEED_TIME = 1
        config.HTTP_LOADER_CURL_LOW_SPEED_LIMIT = 1000000000
        ctx = Context(None, config, None)

        result = await loader.load(ctx, url)
        assert isinstance(result, LoaderResult)
        assert result.buffer is None
        assert not result.successful


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
        assert isinstance(result, LoaderResult)
        assert result.buffer == b"Hello"
        assert result.successful
