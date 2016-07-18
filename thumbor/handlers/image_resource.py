#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com
import datetime

from thumbor.handlers import ImageApiHandler
from thumbor.engines import BaseEngine
import tornado.gen as gen
import tornado.web


##
# Handler to retrieve or modify existing images
# This handler support GET, PUT and DELETE method to manipulate existing images
##
class ImageResourceHandler(ImageApiHandler):

    @gen.coroutine
    def check_resource(self, id):
        id = id[:self.context.config.MAX_ID_LENGTH]
        # Check if image exists
        exists = yield gen.maybe_future(self.context.modules.storage.exists(id))

        if exists:
            body = yield gen.maybe_future(self.context.modules.storage.get(id))
            self.set_status(200)

            mime = BaseEngine.get_mimetype(body)
            if mime:
                self.set_header('Content-Type', mime)

            max_age = self.context.config.MAX_AGE
            if max_age:
                self.set_header('Cache-Control', 'max-age=' + str(max_age) + ',public')
                self.set_header('Expires', datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age))
            self.write(body)
            self.finish()
        else:
            self._error(404, 'Image not found at the given URL')

    def put(self, id):
        id = id[:self.context.config.MAX_ID_LENGTH]
        # Check if image overwriting is allowed
        if not self.context.config.UPLOAD_PUT_ALLOWED:
            self._error(405, 'Unable to modify an uploaded image')
            return

        # Check if the image uploaded is valid
        if self.validate(self.request.body):
            self.write_file(id, self.request.body)
            self.set_status(204)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def delete(self, id):
        id = id[:self.context.config.MAX_ID_LENGTH]
        # Check if image deleting is allowed
        if not self.context.config.UPLOAD_DELETE_ALLOWED:
            self._error(405, 'Unable to delete an uploaded image')
            return

        # Check if image exists
        exists = yield gen.maybe_future(self.context.modules.storage.exists(id))
        if exists:
            self.context.modules.storage.remove(id)
            self.set_status(204)
        else:
            self._error(404, 'Image not found at the given URL')

    @tornado.web.asynchronous
    def get(self, id):
        self.check_resource(id)

    @tornado.web.asynchronous
    def head(self, id):
        self.check_resource(id)
