#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com
import tornado.web
import tornado.ioloop

from thumbor.handlers.image_process import ImageProcessHandler
from thumbor.handlers.healthcheck import HealthcheckHandler
from thumbor.handlers.upload import UploadHandler
from thumbor.handlers.images import ImagesHandler
from thumbor.handlers.image import ImageHandler
from thumbor.url import Url
from thumbor.handlers.imaging import ImagingHandler

class ThumborServiceApp(tornado.web.Application):

    def __init__(self, context):
        self.context = context

        handlers = [
            (r'/healthcheck', HealthcheckHandler),
        ]

        # TODO Old handler to upload images
        if context.config.UPLOAD_ENABLED:
            handlers.append(
                (r'/upload', UploadHandler, { 'context': context })
            )

        # Handler to upload images (POST).
        handlers.append(
            (r'/image', ImagesHandler, { 'context': context })
        )

        # Handler to retrieve or modify existing images  (GET, PUT, DELETE)
        handlers.append(
            (r'/image/(.*)', ImageHandler, { 'context': context })
        )

        # Imaging handler (GET)
        handlers.append(
            (Url.regex(), ImagingHandler, { 'context':  context })
        )

        super(ThumborServiceApp, self).__init__(handlers)
