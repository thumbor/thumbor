#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com
import tornado.web
import tornado.ioloop

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

        if context.config.UPLOAD_ENABLED:
            # TODO Old handler to upload images
            handlers.append(
                (r'/upload', UploadHandler, {'context': self.context})
            )

            # Handler to upload images (POST).
            handlers.append(
                (r'/image', ImagesHandler, {'context': self.context})
            )

            # Handler to retrieve or modify existing images  (GET, PUT, DELETE)
            handlers.append(
                (r'/image/(.*)', ImageHandler, {'context': self.context})
            )

        # Imaging handler (GET)
        handlers.append(
            (Url.regex(), ImagingHandler, {'context': self.context})
        )

        super(ThumborServiceApp, self).__init__(handlers)
