#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect
from tornado_pyvows.context import TornadoHTTPContext

import tornado.web
from thumbor.app import ThumborServiceApp
from thumbor.importer import Importer
from thumbor.config import Config
from thumbor.context import Context
from thumbor.handlers import ContextHandler


@Vows.batch
class CustomHandlerCheck(TornadoHTTPContext):
    def get_app(self):
        cfg = Config()
        cfg.CUSTOM_HANDLERS = ['vows.custom_handler_vows']

        importer = Importer(cfg)
        importer.import_modules()

        ctx = Context(None, cfg, importer)
        application = ThumborServiceApp(ctx)
        return application

    class WhenRunning(TornadoHTTPContext):
        def topic(self):
            response = self.get('/hi/folks')
            return (response.code, response.body)

        class StatusCode(TornadoHTTPContext):
            def topic(self, response):
                return response[0]

            def should_not_be_an_error(self, topic):
                expect(topic).to_equal(200)

        class Body(TornadoHTTPContext):
            def topic(self, response):
                return response[1]

            def should_equal_working(self, topic):
                expect(topic).to_equal('Hello folks!')

    class HeadHandler(TornadoHTTPContext):
        def topic(self):
            response = self.head('/hi/folks')
            return (response.code, response.body)

        class StatusCode(TornadoHTTPContext):
            def topic(self, response):
                return response[0]

            def should_not_be_an_error(self, topic):
                expect(topic).to_equal(200)

class HttpHandler(ContextHandler):

    @classmethod
    def url_regex(cls):
        return '/hi/(?P<name>[^/]+)'

    def get(self, **kw):
        self.write("Hello %s!" % kw["name"])

    def head(self, **kw):
        self.write("Hello %s!" % kw["name"])
