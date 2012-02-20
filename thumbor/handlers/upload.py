#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.handlers import ContextHandler

class UploadHandler(ContextHandler):

    def post(self):
        pass

    def put(self):
        if not 'media' in self.request.files: raise RuntimeError("File was not uploaded properly.")
        if not self.request.files['media']: raise RuntimeError("File was not uploaded properly.")

        file_data = self.request.files['media'][0]
        body = file_data['body']
        filename = file_data['filename']

        storage = self.context.modules.original_photo_storage
        path = storage.resolve_original_photo_path(filename)
        normalized_path = storage.normalize_path(path)
        storage.put(path, body)

        self.write(normalized_path)

