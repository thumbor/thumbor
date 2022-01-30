#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import tornado.ioloop
import tornado.web
from libthumbor.url import Url  # type: ignore

from thumbor.handlers.imaging import ImagingHandler


class ThumborServiceApp(tornado.web.Application):
    def __init__(self, context):
        self.context = context
        self.debug = getattr(self.context.server, "debug", False)
        super().__init__(self.get_handlers(), debug=self.debug)

    def get_handlers(self):
        handlers = []

        for handler_list in self.context.modules.importer.handler_lists:
            get_handlers = getattr(handler_list, "get_handlers", None)

            if get_handlers is None:
                continue
            handlers.extend(get_handlers(self.context))

        # Imaging handler (GET)
        handlers.append(
            (Url.regex(), ImagingHandler, {"context": self.context})
        )

        return handlers
