#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import abspath, join, dirname
from preggy import expect
import mock
# from tornado.concurrent import Future
import tornado.web
from tests.base import PythonTestCase, TestCase
from tornado.concurrent import Future

import thumbor.loaders.http_loader as loader
from thumbor.context import Context
from thumbor.config import Config
from thumbor.media import Media
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


class ReturnContentTestCase(PythonTestCase):

    def test_return_none_on_error(self):
        response_mock = ResponseMock(error='Error', code=599)
        callback_mock = mock.Mock()
        ctx = Context(None, None, None)
        loader.return_contents(response_mock, 'some-url', callback_mock, ctx)
        result = callback_mock.call_args[0][0]
        expect(result).to_be_instance_of(Media)
        expect(result.buffer).to_be_null()
        expect(result.is_valid).to_be_false()

    def test_return_body_if_valid(self):
        response_mock = ResponseMock(body='body', code=200)
        callback_mock = mock.Mock()
        ctx = Context(None, None, None)
        loader.return_contents(response_mock, 'some-url', callback_mock, ctx)
        result = callback_mock.call_args[0][0]
        expect(result).to_be_instance_of(Media)
        expect(result.buffer).to_equal('body')

    def test_return_upstream_error_on_body_none(self):
        response_mock = ResponseMock(body=None, code=200)
        callback_mock = mock.Mock()
        ctx = Context(None, None, None)
        loader.return_contents(response_mock, 'some-url', callback_mock, ctx)
        result = callback_mock.call_args[0][0]
        expect(result).to_be_instance_of(Media)
        expect(result.buffer).to_be_null()
        expect(result.is_valid).to_be_false()
        expect(result.errors).to_include(LoaderResult.ERROR_UPSTREAM)

    def test_return_upstream_error_on_body_empty(self):
        response_mock = ResponseMock(body='', code=200)
        callback_mock = mock.Mock()
        ctx = Context(None, None, None)
        loader.return_contents(response_mock, 'some-url', callback_mock, ctx)
        result = callback_mock.call_args[0][0]
        expect(result).to_be_instance_of(Media)
        expect(result.buffer).to_be_null()
        expect(result.is_valid).to_be_false()
        expect(result.errors).to_include(LoaderResult.ERROR_UPSTREAM)


class ValidateUrlTestCase(PythonTestCase):

    def test_with_allowed_sources(self):
        config = Config()
        config.ALLOWED_SOURCES = ['s.glbimg.com']
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

    def test_should_normalize_url_but_keep_quotes_after_the_domain(self):
        for url in ['http://some.url/my image', 'some.url/my%20image']:
            expect(loader._normalize_url(url)).to_equal('http://some.url/my%20image')

    def test_should_normalize_unicode_urls(self):
        for url in [
            u'https://s3.amazonaws.com/game-screenshots/star_wars\u2122_kotor_cover.png',
            u'https://s3.amazonaws.com/game-screenshots/star_wars™_kotor_cover.png'
        ]:
            expect(loader._normalize_url(url)).\
                to_equal('https://s3.amazonaws.com/game-screenshots/star_wars%E2%84%A2_kotor_cover.png')

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

    def test_load_with_callback(self):
        url = self.get_url('/')
        config = Config()
        ctx = Context(None, config, None)

        loader.load(ctx, url, self.stop)
        result = self.wait()
        expect(result).to_be_instance_of(Media)
        expect(result.buffer).to_equal('Hello')
        expect(result.is_valid).to_be_true()

    def test_load_with_curl(self):
        url = self.get_url('/')
        config = Config()
        config.HTTP_LOADER_CURL_ASYNC_HTTP_CLIENT = True
        ctx = Context(None, config, None)

        loader.load(ctx, url, self.stop)
        result = self.wait()
        expect(result).to_be_instance_of(Media)
        expect(result.buffer).to_equal('Hello')
        expect(result.is_valid).to_be_true()

    def test_should_return_a_future(self):
        url = self.get_url('/')
        config = Config()
        ctx = Context(None, config, None)

        future = loader.load(ctx, url)
        expect(isinstance(future, Future)).to_be_true()


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
        expect(result).to_be_instance_of(Media)
        expect(result.buffer).to_equal('test-user-agent')

    def test_load_with_default_user_agent(self):
        url = self.get_url('/')
        config = Config()
        config.HTTP_LOADER_FORWARD_USER_AGENT = True
        config.HTTP_LOADER_DEFAULT_USER_AGENT = "DEFAULT_USER_AGENT"
        ctx = Context(None, config, None, HandlerMock({}))

        loader.load(ctx, url, self.stop)
        result = self.wait()
        expect(result).to_be_instance_of(Media)
        expect(result.buffer).to_equal('DEFAULT_USER_AGENT')
