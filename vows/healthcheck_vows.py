#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect
from tornado_pyvows.context import TornadoHTTPContext

from thumbor.app import ThumborServiceApp
from thumbor.config import Config
from thumbor.context import Context

@Vows.batch
class HealthCheck(TornadoHTTPContext):
    def get_app(self):
        cfg = Config()
        ctx = Context(None, cfg, None)
        application = ThumborServiceApp(ctx)
        return application

    class WhenRunning(TornadoHTTPContext):
        def topic(self):
            response = self.get('/healthcheck')
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
                expect(topic.lower().strip()).to_equal('working')

