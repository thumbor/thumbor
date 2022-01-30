#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

# Test file
# pylint: disable=protected-access,line-too-long

from os.path import abspath, dirname, join

import tornado.web
from preggy import expect
from tornado.testing import gen_test

import thumbor.loaders.strict_https_loader as loader
from tests.base import TestCase
from thumbor.config import Config
from thumbor.context import Context
from thumbor.loaders import LoaderResult


def fixture_for(filename):
    return abspath(join(dirname(__file__), "fixtures", filename))


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello")


class EchoUserAgentHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(self.request.headers["User-Agent"])


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
    @gen_test
    async def test_return_none_on_error(self):
        response_mock = ResponseMock(error="Error", code=599)
        ctx = Context(None, None, None)
        result = loader.return_contents(response_mock, "some-url", ctx)
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_be_null()
        expect(result.successful).to_be_false()

    @gen_test
    async def test_return_body_if_valid(self):
        response_mock = ResponseMock(body="body", code=200)
        ctx = Context(None, None, None)
        result = loader.return_contents(response_mock, "some-url", ctx)
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal("body")

    @gen_test
    async def test_return_upstream_error_on_body_none(self):
        response_mock = ResponseMock(body=None, code=200)
        ctx = Context(None, None, None)
        result = loader.return_contents(response_mock, "some-url", ctx)
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_be_null()
        expect(result.successful).to_be_false()
        expect(result.error).to_equal(LoaderResult.ERROR_UPSTREAM)

    @gen_test
    async def test_return_upstream_error_on_body_empty(self):
        response_mock = ResponseMock(body="", code=200)
        ctx = Context(None, None, None)
        result = loader.return_contents(response_mock, "some-url", ctx)
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_be_null()
        expect(result.successful).to_be_false()
        expect(result.error).to_equal(LoaderResult.ERROR_UPSTREAM)


class ValidateUrlTestCase(TestCase):
    @gen_test
    async def test_with_allowed_sources(self):
        config = Config()
        config.ALLOWED_SOURCES = ["s.glbimg.com"]
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
                "/glob=:sfoir%20%20%3Co-pmb%20%20%20%20_%20%20%20%200%20%20g.-%3E%3Ca%20hplass=",  # NOQA
            )
        ).to_be_false()
        expect(
            loader.validate(ctx, "https://s.glbimg.com/logo.jpg")
        ).to_be_true()

    @gen_test
    async def test_without_allowed_sources(self):
        config = Config()
        config.ALLOWED_SOURCES = []
        ctx = Context(None, config, None)
        is_valid = loader.validate(ctx, "https://www.google.com/logo.jpg")
        expect(is_valid).to_be_true()

        is_valid = loader.validate(ctx, "http://www.google.com/logo.jpg")
        expect(is_valid).to_be_false()


class NormalizeUrlTestCase(TestCase):
    @gen_test
    async def test_should_normalize_url(self):
        expect(loader._normalize_url("https://some.url")).to_equal(
            "https://some.url"
        )
        expect(loader._normalize_url("some.url")).to_equal("https://some.url")

    @gen_test
    async def test_should_normalize_quoted_url(self):
        url = "https%3A//www.google.ca/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png"  # NOQA
        expected = "https://www.google.ca/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png"  # NOQA
        result = loader._normalize_url(url)
        expect(result).to_equal(expected)
