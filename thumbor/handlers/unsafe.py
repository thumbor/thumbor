#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import tornado.web

from thumbor.handlers import ContextHandler
from thumbor.context import RequestParameters

class MainHandler(ContextHandler):

    @tornado.web.asynchronous
    def get(self, **kw):

        if not self.validate(kw['image']):
            self._error(404)
            return

        self.context.request = RequestParameters(**kw)
        return self.execute_image_operations()

