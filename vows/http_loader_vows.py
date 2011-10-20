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
from tornado.options import options

import thumbor.loaders.http_loader as loader

fixture_for = lambda filename: abspath(join(dirname(__file__), 'fixtures', filename))

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('Hello')

@Vows.batch
class HttpLoader(TornadoHTTPContext):
    def get_app(self):
        application = tornado.web.Application([
            (r"/", MainHandler),
        ])

        return application

    class ValidateURL(TornadoHTTPContext):
        def topic(self):
            old_sources = options.ALLOWED_SOURCES
            options.ALLOWED_SOURCES = ['s.glbimg.com']
            is_valid = loader.validate('http://www.google.com/logo.jpg')
            options.ALLOWED_SOURCES = old_sources
            return is_valid

        def should_default_to_none(self, topic):
            expect(topic).to_be_false()

        class AllowAll(TornadoHTTPContext):
            def topic(self):
                old_sources = options.ALLOWED_SOURCES
                options.ALLOWED_SOURCES = []
                is_valid = loader.validate('http://www.google.com/logo.jpg')
                options.ALLOWED_SOURCES = old_sources
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
            @Vows.asyncTopic
            def topic(self, callback):
                url = self.get_url('/')
                loader.http_client = self._http_client
                loader.load(url, callback)

            def should_equal_hello(self, topic):
                expect(topic).to_equal('Hello')

