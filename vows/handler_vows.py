#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import tornado.web
from pyvows import Vows, expect
from tornado_pyvows.context import TornadoContext, TornadoSubContext

from thumbor.handler import CryptoHandler

@Vows.batch
class HandlerVows(TornadoContext):
    def _get_app(self):
        application = tornado.web.Application([
            (r"/", CryptoHandler),
        ])
        return application

    class CryptoUrl(TornadoSubContext):
        def topic(self):
            self._http_client.fetch(self._get_url('/'), self._stop)
            response = self._wait()
            return response.body

        def should_not_be_an_error(self, topic):
            expect(topic).not_to_be_an_error()

        def should_be_hello(self, topic):
            expect(topic).to_equal('hello')
