#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from mock import MagicMock
from preggy import expect
from tornado.concurrent import Future

from tests.unit import BaseTestCase
from thumbor.blueprints.loaders.http import HttpLoader


class HttpLoaderTestCase(BaseTestCase):
    def test_fetch_1(self):
        """[HttpLoader.fetch] Tests that fetching works properly"""
        loader = HttpLoader()

        client_mock = MagicMock()
        response_mock = MagicMock()
        response_future = Future()
        response_future.set_result(response_mock)
        client_mock.fetch.return_value = response_future

        url = "some.url.com/image.jpg"
        user_agent = "Some User Agent"
        headers = {"what": "header"}
        prepare_curl_callback_mock = MagicMock()

        config_mock = MagicMock(
            HTTP_LOADER_CONNECT_TIMEOUT=1.0,
            HTTP_LOADER_REQUEST_TIMEOUT=1.0,
            HTTP_LOADER_FOLLOW_REDIRECTS=True,
            HTTP_LOADER_MAX_REDIRECTS=1,
            HTTP_LOADER_PROXY_HOST="",
            HTTP_LOADER_PROXY_PORT=None,
            HTTP_LOADER_PROXY_USERNAME="",
            HTTP_LOADER_PROXY_PASSWORD="",
            HTTP_LOADER_CA_CERTS="",
            HTTP_LOADER_CLIENT_KEY="",
            HTTP_LOADER_CLIENT_CERT="",
            HTTP_LOADER_VALIDATE_CERTS=False,
        )

        response = loader.fetch(
            client_mock,
            url,
            user_agent,
            headers,
            config_mock,
            prepare_curl_callback_mock,
        )

        expect(response.result()).to_equal(response_mock)

    def test_get_http_client_1(self):
        """[HttpLoader.get_http_client] Tests that we get default http client when called without config"""
        loader = HttpLoader()
        config_mock = MagicMock(
            HTTP_LOADER_PROXY_HOST="",
            HTTP_LOADER_PROXY_PORT=None,
            HTTP_LOADER_CURL_ASYNC_HTTP_CLIENT=False,
        )
        client_mock = MagicMock()
        client_factory_mock = MagicMock()
        client_factory_mock.return_value = client_mock

        prepare_curl_callback, client = loader.get_http_client(
            config_mock, client_factory_mock
        )
        expect(prepare_curl_callback).to_be_null()
        expect(client).to_equal(client_mock)

    def test_get_http_client_2(self):
        """[HttpLoader.get_http_client] Tests that we get curl http client when called with proxy"""
        loader = HttpLoader()
        prepare_curl_callback_mock = MagicMock()

        loader._get_prepare_curl_callback = MagicMock()
        loader._get_prepare_curl_callback.return_value = prepare_curl_callback_mock

        loader._configure_client = MagicMock()

        config_mock = MagicMock(
            HTTP_LOADER_PROXY_HOST="something",
            HTTP_LOADER_PROXY_PORT=1234,
            HTTP_LOADER_CURL_ASYNC_HTTP_CLIENT=False,
            HTTP_LOADER_MAX_CLIENTS=10,
        )
        client_mock = MagicMock()
        client_factory_mock = MagicMock()
        client_factory_mock.return_value = client_mock

        prepare_curl_callback, client = loader.get_http_client(
            config_mock, client_factory_mock
        )
        expect(prepare_curl_callback).to_equal(prepare_curl_callback)
        expect(client).to_equal(client_mock)
        loader._configure_client.assert_called_with(
            "tornado.curl_httpclient.CurlAsyncHTTPClient", 10
        )


class NormalizeUrlTestCase(BaseTestCase):
    def test_should_normalize_url(self):
        """[HttpLoader._normalize_url] Tests base case for normalizing some urls"""
        loader = HttpLoader()

        for url in ["http://some.url", "some.url"]:
            expect(loader._normalize_url(url)).to_equal("http://some.url")

    def test_should_normalize_url2(self):
        """[HttpLoader._normalize_url] Tests that normalizing a quoted URL works properly"""
        loader = HttpLoader()

        url = "https%3A//www.google.ca/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png"
        expected = "https://www.google.ca/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png"
        result = loader._normalize_url(url)
        expect(result).to_equal(expected)


class RequestHeadersTestCase(BaseTestCase):
    def test_rh1(self):
        """[HttpLoader.get_request_headers] Tests that empty headers and default user agent are used by default"""
        loader = HttpLoader()
        mock_request = MagicMock()
        mock_config = MagicMock(
            HTTP_LOADER_DEFAULT_USER_AGENT="default user agent",
            HTTP_LOADER_FORWARD_ALL_HEADERS=False,
            HTTP_LOADER_FORWARD_USER_AGENT=False,
            HTTP_LOADER_FORWARD_HEADERS_WHITELIST=None,
        )
        mock_details = MagicMock(config=mock_config)

        user_agent, headers = loader.get_request_headers(mock_request, mock_details)

        expect(user_agent).to_equal("default user agent")
        expect(headers).to_be_empty()

    def test_rh2(self):
        """[HttpLoader.get_request_headers] Tests that when forward all headers is active, headers are forwarded"""
        loader = HttpLoader()
        mock_request = MagicMock(headers={"qwe": "asd"})
        mock_config = MagicMock(
            HTTP_LOADER_DEFAULT_USER_AGENT="default user agent",
            HTTP_LOADER_FORWARD_ALL_HEADERS=True,
            HTTP_LOADER_FORWARD_USER_AGENT=False,
            HTTP_LOADER_FORWARD_HEADERS_WHITELIST=None,
        )
        mock_details = MagicMock(config=mock_config)

        user_agent, headers = loader.get_request_headers(mock_request, mock_details)

        expect(user_agent).to_equal("default user agent")
        expect(headers).to_be_like({"qwe": "asd"})

    def test_rh3(self):
        """[HttpLoader.get_request_headers] Tests that when forward user agent is active, user agent is forwarded"""
        loader = HttpLoader()
        mock_request = MagicMock(headers={"User-Agent": "some user agent"})
        mock_config = MagicMock(
            HTTP_LOADER_DEFAULT_USER_AGENT="default user agent",
            HTTP_LOADER_FORWARD_ALL_HEADERS=False,
            HTTP_LOADER_FORWARD_USER_AGENT=True,
            HTTP_LOADER_FORWARD_HEADERS_WHITELIST=None,
        )
        mock_details = MagicMock(config=mock_config)

        user_agent, headers = loader.get_request_headers(mock_request, mock_details)

        expect(user_agent).to_equal("some user agent")
        expect(headers).to_be_empty()

    def test_rh4(self):
        """[HttpLoader.get_request_headers] Tests whitelisted headers are forwarded"""
        loader = HttpLoader()
        mock_request = MagicMock(headers={"Some-Header": "some value"})
        mock_config = MagicMock(
            HTTP_LOADER_DEFAULT_USER_AGENT="default user agent",
            HTTP_LOADER_FORWARD_ALL_HEADERS=False,
            HTTP_LOADER_FORWARD_USER_AGENT=False,
            HTTP_LOADER_FORWARD_HEADERS_WHITELIST=["Some-Header"],
        )
        mock_details = MagicMock(config=mock_config)

        user_agent, headers = loader.get_request_headers(mock_request, mock_details)

        expect(user_agent).to_equal("default user agent")
        expect(headers).to_be_like({"Some-Header": "some value"})
