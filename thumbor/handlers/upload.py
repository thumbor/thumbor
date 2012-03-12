#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import exists
import urllib

from thumbor.handlers import ContextHandler

class UploadHandler(ContextHandler):

    def write_file(self, filename, body, overwrite):
        storage = self.context.modules.original_photo_storage
        path = storage.resolve_original_photo_path(filename)

        if not overwrite and storage.exists(path):
            raise RuntimeError('File already exists.')

        stored_path = storage.put(path, body)

        return stored_path

    def extract_file_data(self):
        if not 'media' in self.request.files: raise RuntimeError("File was not uploaded properly.")
        if not self.request.files['media']: raise RuntimeError("File was not uploaded properly.")

        return self.request.files['media'][0]

    def save_and_render(self, overwrite=False):
        file_data = self.extract_file_data()
        body = file_data['body']
        filename = file_data['filename']
        path = ""
        try:
            path = self.write_file(filename, body, overwrite=overwrite)
            self.set_status(201)
        except RuntimeError:
            self.set_status(409)
            path = 'File already exists.'
        self.write(path)

    def post(self):
        if self.validate():
            self.save_and_render()
        else:
            self.set_status(412)
            self.write('File is too big, not an image or too small image')

    def put(self):
        if not self.context.config.ALLOW_ORIGINAL_PHOTO_PUTTING: return
        if self.validate():
            self.save_and_render(overwrite=True)
        else:
            self.set_status(412)
            self.write('File is too big, not an image or too small image')

    def delete(self):
        if not self.context.config.ALLOW_ORIGINAL_PHOTO_DELETION: return
        path = 'file_path' in self.request.arguments and self.request.arguments['file_path'] or None
        if path is None and self.request.body is None: raise RuntimeError('The file_path argument is mandatory to delete an image')
        path = urllib.unquote(self.request.body.split('=')[-1])

        if self.context.modules.storage.exists(path):
            self.context.modules.storage.remove(path)

    def validate(self):
        conf = self.context.config
        engine = self.context.modules.engine

        if ( conf.MAX_SIZE != 0 and  len(self.extract_file_data()['body']) > conf.MAX_SIZE ):
            return False

        try:
            engine.load(self.extract_file_data()['body'],None)
        except IOError:
            return False

        size = engine.size
        if (conf.MIN_WIDTH > size[0] or conf.MIN_HEIGHT > size[1]) :
            return False

        return True
