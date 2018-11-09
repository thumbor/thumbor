#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from mock import MagicMock
from preggy import expect

from tests.unit import BaseTestCase
from thumbor.blueprints.loaders.http import HttpLoader


class HttpLoaderTestCase(BaseTestCase):
    pass


class NormalizeUrlTestCase(BaseTestCase):
    def test_should_normalize_url(self):
        """Tests base case for normalizing some urls"""
        loader = HttpLoader()

        for url in ["http://some.url", "some.url"]:
            expect(loader._normalize_url(url)).to_equal("http://some.url")

    def test_should_normalize_url2(self):
        """Tests that normalizing a quoted URL works properly"""
        loader = HttpLoader()

        url = "https%3A//www.google.ca/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png"
        expected = "https://www.google.ca/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png"
        result = loader._normalize_url(url)
        expect(result).to_equal(expected)


class RequestHeadersTestCase(BaseTestCase):
    def test_rh1(self):
        """Tests that empty headers and default user agent are used by default"""
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
        """Tests that when forward all headers is active, headers are forwarded"""
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
        """Tests that when forward user agent is active, user agent is forwarded"""
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
        """Tests whitelisted headers are forwarded"""
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

    # def get_request_headers(self, request, details):
    # user_agent = None
    # headers = {}

    # if details.config.HTTP_LOADER_FORWARD_ALL_HEADERS:
    # headers = request.headers
    # else:
    # if details.config.HTTP_LOADER_FORWARD_USER_AGENT:
    # if "User-Agent" in request.headers:
    # user_agent = request.headers["User-Agent"]

    # if details.config.HTTP_LOADER_FORWARD_HEADERS_WHITELIST:
    # for header_key in details.config.HTTP_LOADER_FORWARD_HEADERS_WHITELIST:
    # if header_key in request.headers:
    # headers[header_key] = request.headers[header_key]

    # if user_agent is None and "User-Agent" not in headers:
    # user_agent = details.config.HTTP_LOADER_DEFAULT_USER_AGENT

    # return user_agent, headers
