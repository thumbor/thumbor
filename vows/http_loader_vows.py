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

import thumbor.loaders.http_loader as loader

fixture_for = lambda filename: abspath(join(dirname(__file__), 'fixtures', filename))

@Vows.assertion
def to_match_contents_of(topic, filepath):
    assert file(filepath).read() == topic, "Expected body of %s to match topic, but it didn't" % filepath

class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        path = fixture_for('conselheira_tutelar.jpg')
        contents = open(path.read())
        self.write(contents)
        self.set_header("Content-Type", "image/jpeg")
        self.finish()

@Vows.batch
class HttpLoader(Vows.Context):
    class NormalizeURL(Vows.Context):
        class WhenStartsWithHttp(Vows.Context):
            def topic(self):
                return loader._normalize_url('http://some.url')

            def should_return_same_url(self, topic):
                expect(topic).to_equal('http://some.url')

        class WhenDoesNotStartWithHttp(Vows.Context):
            def topic(self):
                return loader._normalize_url('some.url')

            def should_return_normalized_url(self, topic):
                expect(topic).to_equal('http://some.url')

    class LoadAndVerifyImage(TornadoContext):
        def _get_app(self):
            application = tornado.web.Application([
                (r"/", MainHandler),
            ])
            loader.http = self._http_client
            return application

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
                loader.load(self._get_url('/'), self._stop)

                result = self._wait()

                return result

            def should_equal_regular_http_get(self, topic):
                expect(topic).to_match_contents_of(fixture_for('conselheira_tutelar.jpg'))
