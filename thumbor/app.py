#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import tornado.ioloop
import tornado.web
from libthumbor.url import Url

from thumbor.handlers.imaging import ImagingHandler


class ThumborServiceApp(tornado.web.Application):
    def __init__(self, context):
        self.context = context
        self.debug = getattr(self.context.server, "debug", False)
        super(ThumborServiceApp, self).__init__(self.get_handlers(), debug=self.debug)

    def get_handlers(self):
        handlers = []
        for router in self.context.modules.importer.routers:
            handlers.extend(
                [
                    (route.url, route.handler, route.initialize)
                    for route in router(self.context).get_routes()
                ]
            )

        # Imaging handler (GET)
        handlers.append((Url.regex(), ImagingHandler, {"context": self.context}))

        return handlers
