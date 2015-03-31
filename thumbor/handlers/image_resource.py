#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com
import datetime

from thumbor.handlers import ImageApiHandler
from thumbor.engines import BaseEngine


##
# Handler to retrieve or modify existing images
# This handler support GET, PUT and DELETE method to manipulate existing images
##
class ImageResourceHandler(ImageApiHandler):

    def check_resource(self, id):
        id = id[:self.context.config.MAX_ID_LENGTH]

        def on_storage_response(body):
            '''Callback for storage.get'''

            self.set_status(200)

            mime = BaseEngine.get_mimetype(body)
            if mime:
                self.set_header('Content-Type', mime)

            max_age = self.context.config.MAX_AGE
            if max_age:
                self.set_header('Cache-Control', 'max-age=' + str(max_age) + ',public')
                self.set_header('Expires', datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age))
            self.write(body)

        def on_storage_exists(exists):
            '''Callback for storage.exists'''

            # Check if image exists
            if exists:
                self.context.modules.storage.get(id, on_storage_response)
            else:
                self._error(404, 'Image not found at the given URL')

        self.context.modules.storage.exists(id, on_storage_exists)

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

    def delete(self, id):
        id = id[:self.context.config.MAX_ID_LENGTH]
        # Check if image deleting is allowed
        if not self.context.config.UPLOAD_DELETE_ALLOWED:
            self._error(405, 'Unable to delete an uploaded image')
            return

        def on_storage_response(exists):
            # Check if image exists
            if exists:
                self.context.modules.storage.remove(id)
                self.set_status(204)
            else:
                self._error(404, 'Image not found at the given URL')
        self.context.modules.storage.exists(id, on_storage_response)

    def get(self, id):
        self.check_resource(id)

    def head(self, id):
        self.check_resource(id)
