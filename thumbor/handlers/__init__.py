#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com


import datetime
import traceback

import tornado.gen as gen
import tornado.web

from thumbor.context import Context
from thumbor.engines import BaseEngine
from thumbor.utils import logger

try:
    basestring  # Python 2
except NameError:
    basestring = str  # Python 3


class BaseHandler(tornado.web.RequestHandler):
    pass


class ContextHandler(BaseHandler):
    def prepare(self, *args, **kwargs):
        super(BaseHandler, self).prepare(*args, **kwargs)

        self._response_ext = None
        self._response_length = None

        self._response_start = datetime.datetime.now()
        self.context.metrics.incr('response.count')

    def on_finish(self, *args, **kwargs):
        super(BaseHandler, self).on_finish(*args, **kwargs)

        total_time = (datetime.datetime.now() - self._response_start).total_seconds() * 1000
        status = self.get_status()
        self.context.metrics.timing('response.time', total_time)
        self.context.metrics.timing('response.time.{0}'.format(status), total_time)
        self.context.metrics.incr('response.status.{0}'.format(status))

        if self._response_ext is not None:
            ext = self._response_ext
            self.context.metrics.incr('response.format{0}'.format(ext))
            self.context.metrics.timing('response.time{0}'.format(ext), total_time)
            if self._response_length is not None:
                self.context.metrics.incr('response.bytes{0}'.format(ext), self._response_length)

        self.context.request_handler = None
        if hasattr(self.context, 'request') and hasattr(self.context.request, 'engine'):
            self.context.request.engine = None
        self.context.modules = None
        self.context.filters_factory = None
        self.context.metrics = None
        self.context.thread_pool = None
        self.context.transformer = None
        self.context = None

    def initialize(self, context):
        self.context = Context(
            server=context.server,
            config=context.config,
            importer=context.modules.importer,
            request_handler=self
        )
        self.context.metrics.initialize(self)

    def log_exception(self, *exc_info):
        if isinstance(exc_info[1], tornado.web.HTTPError):
            # Delegate HTTPError's to the base class
            # We don't want these through normal exception handling
            return super(ContextHandler, self).log_exception(*exc_info)

        msg = traceback.format_exception(*exc_info)

        try:
            if self.context.config.USE_CUSTOM_ERROR_HANDLING:
                self.context.modules.importer.error_handler.handle_error(context=self.context, handler=self,
                                                                         exception=exc_info)
        finally:
            del exc_info
            logger.error('ERROR: %s' % "".join(msg))

    @gen.coroutine
    def get_blacklist_contents(self):
        filename = 'blacklist.txt'

        exists = yield gen.maybe_future(self.context.modules.storage.exists(filename))
        if exists:
            blacklist = yield gen.maybe_future(self.context.modules.storage.get(filename))
            raise tornado.gen.Return(blacklist)
        else:
            raise tornado.gen.Return("")


##
# Base handler for Image API operations
##
class ImageApiHandler(ContextHandler):
    def validate(self, body):
        conf = self.context.config
        mime = BaseEngine.get_mimetype(body)

        if mime == 'image/gif' and self.context.config.USE_GIFSICLE_ENGINE:
            engine = self.context.modules.gif_engine
        else:
            engine = self.context.modules.engine

        # Check if image is valid
        try:
            engine.load(body, None)
        except IOError:
            raise tornado.web.HTTPError(415, 'Unsupported Media Type')

        # Check weight constraints
        if conf.UPLOAD_MAX_SIZE != 0 and len(self.request.body) > conf.UPLOAD_MAX_SIZE:
            raise tornado.web.HTTPError(
                412,
                'Image exceed max weight (Expected : %s, Actual : %s)' % (conf.UPLOAD_MAX_SIZE, len(self.request.body)))

        # Check size constraints
        size = engine.size
        if conf.MIN_WIDTH > size[0] or conf.MIN_HEIGHT > size[1]:
            raise tornado.web.HTTPError(412, 'Image is too small (Expected: %s/%s , Actual : %s/%s)' % (
                conf.MIN_WIDTH, conf.MIN_HEIGHT, size[0], size[1]))

        return True

    def write_file(self, id, body):
        storage = self.context.modules.upload_photo_storage
        storage.put(id, body)
