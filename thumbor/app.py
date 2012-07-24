#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import tornado.web
import tornado.ioloop

from thumbor.handlers.image import ImageProcessHandler
from thumbor.handlers.healthcheck import HealthcheckHandler
from thumbor.handlers.upload import UploadHandler
from thumbor.url import Url

class ThumborServiceApp(tornado.web.Application):

    def __init__(self, context):
        self.context = context

        handlers = [
            (r'/healthcheck', HealthcheckHandler),
        ]

        if context.config.UPLOAD_ENABLED:
            handlers.append(
                (r'/upload', UploadHandler, { 'context': context })
            )

        handlers.append(
            (Url.regex(), ImageProcessHandler, { 'context':  context })
        )

        super(ThumborServiceApp, self).__init__(handlers)
