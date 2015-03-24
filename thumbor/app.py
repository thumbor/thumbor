#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com
import tornado.web
import tornado.ioloop

from thumbor.handlers.blacklist import BlacklistHandler
from thumbor.handlers.healthcheck import HealthcheckHandler
from thumbor.handlers.legacy_upload import LegacyImageUploadHandler
from thumbor.handlers.upload import ImageUploadHandler
from thumbor.handlers.image_resource import ImageResourceHandler
from thumbor.url import Url
from thumbor.handlers.imaging import ImagingHandler


class ThumborServiceApp(tornado.web.Application):

    def __init__(self, context):
        '''Initialize the ThumborServiceApp with the given context.

        :param context: The thumbor execution context.
        :type context: thumbor.context.Context
        '''

        self.context = context
        super(ThumborServiceApp, self).__init__(self.get_handlers())

    def get_handlers(self):
        '''Returns a list of Tornado HTTP handlers.

        :returns: A list of Tornado HTTP handlers
        :rtype: list
        '''

        handlers = [
            (r'/healthcheck', HealthcheckHandler),
        ]

        if self.context.config.UPLOAD_ENABLED:
            # TODO: Old handler to upload images. Will be deprecated soon.
            handlers.append(
                (r'/upload', LegacyImageUploadHandler, {'context': self.context})
            )

            # Handler to upload images (POST).
            handlers.append(
                (r'/image', ImageUploadHandler, {'context': self.context})
            )

            # Handler to retrieve or modify existing images  (GET, PUT, DELETE)
            handlers.append(
                (r'/image/(.*)', ImageResourceHandler, {'context': self.context})
            )

        if self.context.config.USE_BLACKLIST:
            handlers.append(
                (r'/blacklist', BlacklistHandler, {'context': self.context})
            )

        # Imaging handler (GET)
        handlers.append(
            (Url.regex(), ImagingHandler, {'context': self.context})
        )

        return handlers
