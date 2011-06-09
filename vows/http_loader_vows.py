#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import abspath, join, dirname

from pyvows import Vows, expect
from tornado_pyvows.context import TornadoContext, TornadoSubContext
import tornado.web
from tornado.options import options

import thumbor.loaders.http_loader as loader

fixture_for = lambda filename: abspath(join(dirname(__file__), 'fixtures', filename))

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('Hello')

application = tornado.web.Application([
    (r"/", MainHandler),
])

@Vows.batch
class HttpLoader(TornadoContext):
    def _get_app(self):
        loader.http_client = self._http_client
        return application

    class ValidateURL(TornadoSubContext):
        def topic(self):
            return loader.validate('http://www.google.com/logo.jpg')

        def should_default_to_none(self, topic):
            expect(topic).to_be_true()

        class AllowAll(TornadoSubContext):
            def topic(self):
                old_sources = options.ALLOWED_SOURCES
                options.ALLOWED_SOURCES = []
                is_valid = loader.validate('http://www.google.com/logo.jpg')
                options.ALLOWED_SOURCES = old_sources
                return is_valid

            def should_validate(self, topic):
                expect(topic).to_be_true()

    class NormalizeURL(TornadoSubContext):
        class WhenStartsWithHttp(TornadoSubContext):
            def topic(self):
                return loader._normalize_url('http://some.url')

            def should_return_same_url(self, topic):
                expect(topic).to_equal('http://some.url')

        class WhenDoesNotStartWithHttp(TornadoSubContext):
            def topic(self):
                return loader._normalize_url('some.url')

            def should_return_normalized_url(self, topic):
                expect(topic).to_equal('http://some.url')

    class LoadAndVerifyImage(TornadoSubContext):
        #class Verify(Vows.Context):
            #class WhenInMaxSize(Vows.Context):
                #def topic(self, url):
                    #return verify_size(url, 50 * 1024)

                #def should_return_true_to_fifty_megs(self, topic):
                    #expect(topic).to_be_true()

            #class WhenOutOfMaxSize(Vows.Context):
                #def topic(self, url):
                    #return verify_size(url, 1)

                #def should_return_false_to_one_kb(self, topic):
                    #expect(topic).to_be_false()

        class Load(TornadoSubContext):
            def topic(self):
                url = self._get_url('/')
                loader.load(url, self._stop)
                result = self._wait()

                return result

            def should_equal_hello(self, topic):
                expect(topic).to_equal('Hello')

