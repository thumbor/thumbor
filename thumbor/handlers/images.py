#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import uuid
import mimetypes
from thumbor.handlers import  ImageApiHandler


##
# Handler to upload images.
# This handler support only POST method, but images can be uploaded  :
#   - through multipart/form-data (designed for forms)
#   - or with the image content in the request body (rest style)
##

class ImagesHandler(ImageApiHandler):

    def post(self):
        # Check if the image uploaded is a multipart/form-data
        if self.multipart_form_data():
            file_data = self.request.files['media'][0]
            body = file_data['body']

            # Retrieve filename from 'filename' field
            filename = file_data['filename']
        else:
            body = self.request.body

            # Retrieve filename from 'Slug' header
            filename = self.request.headers.get('Slug')

        # Check if the image uploaded is valid
        if self.validate(body):

            # Use the default filename for the uploaded images
            if not filename:
                content_type = self.request.headers.get('Content-Type', self.get_mimetype(body))
                extension = mimetypes.guess_extension(content_type, False)
                if extension == '.jpe': extension = '.jpg'          # Hack because mimetypes return .jpe by default
                filename = self.context.config.UPLOAD_DEFAULT_FILENAME + extension

            # Build image id based on a random uuid (32 characters)
            id = str(uuid.uuid4().hex)
            self.write_file(id, body)
            self.set_status(201)
            self.set_header('Location', self.location(id, filename))

    def multipart_form_data(self):
        if not 'media' in self.request.files or not self.request.files['media']:
            return False
        else:
            return True

    def location(self, id, filename):
        base_uri = self.request.uri
        return base_uri + '/' + id + '/' + filename


