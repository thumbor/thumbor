#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

'''
Handler responsible for:
    * Thumbor's image requests;
    * Thumbor's metadata requests.
'''

import tornado.web
import tornado.gen

import thumbor.context


class CoreHandler(tornado.web.RequestHandler):

    @tornado.gen.coroutine
    def get(self, **kw):
        req = thumbor.context.RequestParameters.from_route_arguments(self.request, kw)

        req = None
