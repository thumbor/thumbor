#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from os.path import abspath, dirname, join

import tornado.web
from preggy import expect
from tornado.testing import gen_test

import thumbor.loaders.https_loader as loader
from tests.base import TestCase
from thumbor.config import Config
from thumbor.context import Context
from thumbor.loaders import LoaderResult

# test code
# pylint: disable=abstract-method,too-few-public-methods,protected-access


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
                "/glob=:sfoir%20%20%3Co-pmb%20%20%20%20_%20%20%20%200%20%20g.-%3E%3Ca%20hplass=",  # NOQA, pylint:disable=line-too-long
            )
        ).to_be_false()
        expect(
            loader.validate(ctx, "http://s.glbimg.com/logo.jpg")
        ).to_be_true()

    @gen_test
    async def test_without_allowed_sources(self):
        config = Config()
        config.ALLOWED_SOURCES = []
        ctx = Context(None, config, None)
        is_valid = loader.validate(ctx, "http://www.google.com/logo.jpg")
        expect(is_valid).to_be_true()


class NormalizeUrlTestCase(TestCase):
    @gen_test
    async def test_should_normalize_url(self):
        expect(loader._normalize_url("http://some.url")).to_equal(
            "http://some.url"
        )
        expect(loader._normalize_url("some.url")).to_equal("https://some.url")

    @gen_test
    async def test_should_normalize_quoted_url(self):
        url = (
            "https%3A//www.google.ca/images/branding/googlelogo/2x/"
            "googlelogo_color_272x92dp.png"
        )
        expected = (
            "https://www.google.ca/images/branding/googlelogo/2x/"
            "googlelogo_color_272x92dp.png"
        )
        result = loader._normalize_url(url)
        expect(result).to_equal(expected)


class HttpsLoaderTestCase(TestCase):
    def get_app(self):
        application = tornado.web.Application([(r"/", MainHandler)])

        return application

    @gen_test
    async def test_load(self):
        url = self.get_url("/")
        config = Config()
        ctx = Context(None, config, None)

        result = await loader.load(ctx, url)
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal("Hello")
        expect(result.successful).to_be_true()

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


class HttpLoaderWithUserAgentForwardingTestCase(TestCase):
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
