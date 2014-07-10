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

    def put(self, id):
        id = id[:32]
        # Check if image overwriting is allowed
        if not self.context.config.UPLOAD_PUT_ALLOWED:
            self._error(405, 'Unable to modify an uploaded image')
            return

        # Check if the image uploaded is valid
        if self.validate(self.request.body):
            self.write_file(id, self.request.body)
            self.set_status(204)

    def delete(self, id):
        id = id[:32]
        # Check if image deleting is allowed
        if not self.context.config.UPLOAD_DELETE_ALLOWED:
            self._error(405, 'Unable to delete an uploaded image')
            return

        # Check if image exists
        if self.context.modules.storage.exists(id):
            self.context.modules.storage.remove(id)
            self.set_status(204)
        else:
            self._error(404, 'Image not found at the given URL')

    def get(self, id):
        id = id[:32]
        # Check if image exists
        if self.context.modules.storage.exists(id):
            body = self.context.modules.storage.get(id)
            self.set_status(200)

            mime = BaseEngine.get_mimetype(body)
            if mime:
                self.set_header('Content-Type', mime)

            max_age = self.context.config.MAX_AGE
            if max_age:
                self.set_header('Cache-Control', 'max-age=' + str(max_age) + ',public')
                self.set_header('Expires', datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age))
            self.write(body)
        else:
            self._error(404, 'Image not found at the given URL')
