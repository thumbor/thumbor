#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect
from tornado_pyvows.context import TornadoContext, TornadoSubContext

from thumbor.app import ThumborServiceApp

@Vows.batch
class HealthCheck(TornadoContext):
    def _get_app(self):
        application = ThumborServiceApp()
        return application

    class WhenRunning(TornadoSubContext):
        def topic(self):
            self._http_client.fetch(self._get_url('/healthcheck'), self._stop)
            response = self._wait()

            return (response.code, response.body)

        class StatusCode(TornadoSubContext):
            def topic(self, response):
                return response[0]

            def should_not_be_an_error(self, topic):
                expect(topic).to_equal(200)

        class Body(TornadoSubContext):
            def topic(self, response):
                return response[1]

            def should_equal_working(self, topic):
                expect(topic).to_equal('working')

