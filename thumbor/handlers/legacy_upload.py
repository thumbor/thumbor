#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import urllib

from thumbor.handlers import ContextHandler
import tornado.gen


class BadRequestError(ValueError):
    pass


class LegacyImageUploadHandler(ContextHandler):

    @tornado.gen.coroutine
    def write_file(self, filename, body, overwrite):
        storage = self.context.modules.upload_photo_storage
        path = filename
        if hasattr(storage, 'resolve_original_photo_path'):
            path = storage.resolve_original_photo_path(self.request, filename)

        exists = yield storage.exists(path)
        if not overwrite and exists:
            raise RuntimeError('File already exists.')

        stored_path = storage.put(path, body)

        raise tornado.gen.Return(stored_path)

    def extract_file_data(self):
        if 'media' not in self.request.files:
            raise RuntimeError("File was not uploaded properly.")
        if not self.request.files['media']:
            raise RuntimeError("File was not uploaded properly.")

        return self.request.files['media'][0]

    @tornado.gen.coroutine
    def save_and_render(self, overwrite=False):
        file_data = self.extract_file_data()
        body = file_data['body']
        filename = file_data['filename']
        path = ""
        try:
            path = yield self.write_file(filename, body, overwrite=overwrite)
            self.set_status(201)
            self.set_header('Location', path)
        except RuntimeError:
            self.set_status(409)
            path = 'File already exists.'
        except BadRequestError:
            self.set_status(400)
            path = 'Invalid request'

        self.write(path)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        if self.validate():
            yield self.save_and_render()
        else:
            self.set_status(412)
            self.write('File is too big, not an image or too small image')

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def put(self):
        if not self.context.config.UPLOAD_PUT_ALLOWED:
            self.set_status(405)
            return

        if self.validate():
            yield self.save_and_render(overwrite=True)
        else:
            self.set_status(412)
            self.write('File is too big, not an image or too small image')

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def delete(self):
        if not self.context.config.UPLOAD_DELETE_ALLOWED:
            self.set_status(405)
            return

        path = 'file_path' in self.request.arguments and self.request.arguments['file_path'] or None
        if path is None and self.request.body is None:
            raise RuntimeError('The file_path argument is mandatory to delete an image')

        path = urllib.unquote(self.request.body.split('=')[-1])

        exists = yield self.context.modules.storage.exists(path)
        if exists:
            self.context.modules.storage.remove(path)

    def validate(self):
        conf = self.context.config
        engine = self.context.modules.engine

        if (conf.UPLOAD_MAX_SIZE != 0 and len(self.extract_file_data()['body']) > conf.UPLOAD_MAX_SIZE):
            return False

        try:
            engine.load(self.extract_file_data()['body'], None)
        except IOError:
            return False

        size = engine.size
        if (conf.MIN_WIDTH > size[0] or conf.MIN_HEIGHT > size[1]):
            return False

        return True
