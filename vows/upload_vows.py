#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import mimetypes
import urllib
from os.path import abspath, join, dirname, exists
from datetime import datetime
from shutil import rmtree

from pyvows import Vows, expect
from tornado_pyvows.context import TornadoHTTPContext

from thumbor.app import ThumborServiceApp
from thumbor.config import Config
from thumbor.importer import Importer
from thumbor.context import Context

storage_path = '/tmp/thumbor-vows/storage'
crocodile_file_path = abspath(join(dirname(__file__), 'crocodile.jpg'))
oversized_file_path = abspath(join(dirname(__file__), 'fixtures/image.jpg'))

if exists(storage_path):
    rmtree(storage_path)

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

"adapted from: http://code.activestate.com/recipes/146306/"
def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form
fields.
    files is a sequence of (name, filename, value) elements for data
to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----thumborUploadFormBoundary'
    CRLF = '\r\n'
    L = []
    for key, value in fields.iteritems():
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('')
    L.append('')
    L.append(BOUNDARY + '--')

    body = CRLF.join([str(item) for item in L])

    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY

    return content_type, body

class BaseContext(TornadoHTTPContext):
    def __init__(self, *args, **kw):
        super(BaseContext, self).__init__(*args, **kw)
        self.ignore('post_files', 'delete')

    def delete(self, path, data={}):
        return self.fetch(path, method="DELETE", body=urllib.urlencode(data, doseq=True), allow_nonstandard_methods=True)

    def post_files(self, method, path, data={}, files=[]):
        multipart_data = encode_multipart_formdata(data, files)

        return self.fetch(path,
            method=method.upper(),
            body=multipart_data[1],
            headers={
                'Content-Type': multipart_data[0]
            },
            allow_nonstandard_methods=True)

@Vows.batch
class Upload(BaseContext):
    def get_app(self):
        cfg = Config()
        cfg.ENABLE_ORIGINAL_PHOTO_UPLOAD = True
        cfg.ORIGINAL_PHOTO_STORAGE = 'thumbor.storages.file_storage'
        cfg.FILE_STORAGE_ROOT_PATH = storage_path
        cfg.ALLOW_ORIGINAL_PHOTO_DELETION = True
        cfg.ALLOW_ORIGINAL_PHOTO_PUTTING = True

        importer = Importer(cfg)
        importer.import_modules()
        ctx = Context(None, cfg, importer)
        application = ThumborServiceApp(ctx)
        return application

    class WhenPutting(BaseContext):
        def topic(self):
            with open(crocodile_file_path, 'r') as croc:
                image = ('media', u'crocodile.jpg', croc.read())
            response = self.post_files('put', '/upload', {}, (image, ))
            return (response.code, response.body)

        class StatusCode(TornadoHTTPContext):
            def topic(self, response):
                return response[0]

            def should_not_be_an_error(self, topic):
                expect(topic).to_equal(201)

        class Body(TornadoHTTPContext):
            def topic(self, response):
                return response[1]

            def should_be_in_right_path(self, topic):
                file_path = join(datetime.now().strftime('%Y/%m/%d'), 'crocodile.jpg')
                path = join(storage_path, file_path)
                expect(topic).to_equal(file_path)
                expect(exists(path)).to_be_true()

    class WhenPuttingInvalidImage(BaseContext):
        def topic(self):
            image = ('media', u'crocodile9999.jpg', 'toto')
            response = self.post_files('put', '/upload', {}, (image, ))
            return (response.code, response.body)

        def should_be_an_error(self, topic):
             expect(topic[0]).to_equal(412)

    class WhenPostingInvalidImage(BaseContext):
        def topic(self):
            image = ('media', u'crocodile9999.jpg', 'toto')
            response = self.post_files('post', '/upload', {}, (image, ))
            return (response.code, response.body)

        def should_be_an_error(self, topic):
             expect(topic[0]).to_equal(412)

    class WhenPosting(BaseContext):
        def topic(self):
            with open(crocodile_file_path, 'r') as croc:
                image = ('media', u'crocodile2.jpg', croc.read())
            response = self.post_files('post', '/upload', {}, (image, ))
            return (response.code, response.body)

        class StatusCode(TornadoHTTPContext):
            def topic(self, response):
                return response[0]

            def should_not_be_an_error(self, topic):
                expect(topic).to_equal(201)

        class Body(TornadoHTTPContext):
            def topic(self, response):
                return response[1]

            def should_be_in_right_path(self, topic):
                file_path = join(datetime.now().strftime('%Y/%m/%d'), 'crocodile2.jpg')
                path = join(storage_path, file_path)
                expect(topic).to_equal(file_path)
                expect(exists(path)).to_be_true()

        class WhenRePosting(BaseContext):
            def topic(self):
                with open(crocodile_file_path, 'r') as croc:
                    image = ('media', u'crocodile2.jpg', croc.read())
                response = self.post_files('post', '/upload', {}, (image, ))
                return (response.code, response.body)

            class StatusCode(TornadoHTTPContext):
                def topic(self, response):
                    return response[0]

                def should_be_an_error(self, topic):
                    expect(topic).to_equal(409)

            class WhenDeleting(BaseContext):
                def topic(self):
                    file_path = join(datetime.now().strftime('%Y/%m/%d'), 'crocodile2.jpg')
                    response = self.delete('/upload', {
                        'file_path': file_path
                    })
                    return (response.code, response.body)

                class StatusCode(TornadoHTTPContext):
                    def topic(self, response):
                        return response[0]

                    def should_not_be_an_error_and_file_should_not_exist(self, topic):
                        file_path = join(datetime.now().strftime('%Y/%m/%d'), 'crocodile2.jpg')
                        path = join(storage_path, file_path)
                        expect(topic).to_equal(200)
                        expect(exists(path)).to_be_false()

                class DeletingAgainDoesNothing(BaseContext):
                    def topic(self):
                        file_path = join(datetime.now().strftime('%Y/%m/%d'), 'crocodile2.jpg')
                        response = self.delete('/upload', {
                            'file_path': file_path
                            })
                        return (response.code, response.body)

                    class StatusCode(TornadoHTTPContext):
                        def topic(self, response):
                            return response[0]

                        def should_not_be_an_error_and_file_should_not_exist(self, topic):
                            expect(topic).to_equal(200)

            class DeletingWithInvalidPathDoesNothing(BaseContext):
                def topic(self):
                    file_path = join(datetime.now().strftime('%Y/%m/%d'), 'crocodile5.jpg')
                    response = self.delete('/upload', {
                        'file_path': file_path
                    })
                    return (response.code, response.body)

                class StatusCode(TornadoHTTPContext):
                    def topic(self, response):
                        return response[0]

                    def should_not_be_an_error_and_file_should_not_exist(self, topic):
                        expect(topic).to_equal(200)

@Vows.batch
class UploadWithoutDeletingAllowed(BaseContext):
    def get_app(self):
        cfg = Config()
        cfg.ENABLE_ORIGINAL_PHOTO_UPLOAD = True
        cfg.ORIGINAL_PHOTO_STORAGE = 'thumbor.storages.file_storage'
        cfg.FILE_STORAGE_ROOT_PATH = storage_path
        cfg.ALLOW_ORIGINAL_PHOTO_DELETION = False

        importer = Importer(cfg)
        importer.import_modules()
        ctx = Context(None, cfg, importer)
        application = ThumborServiceApp(ctx)
        return application

    class WhenPosting(BaseContext):
        def topic(self):
            with open(crocodile_file_path, 'r') as croc:
                image = ('media', u'crocodile3.jpg', croc.read())
                response = self.post_files('post', '/upload', {}, (image, ))
                return (response.code, response.body)

        class ThenDeleting(BaseContext):
            def topic(self):
                file_path = join(datetime.now().strftime('%Y/%m/%d'), 'crocodile3.jpg')
                response = self.delete('/upload', {
                'file_path': file_path
                })
                return (response.code, response.body)

            class StatusCode(TornadoHTTPContext):
                def topic(self, response):
                    return response[0]

                def should_not_be_an_error_and_file_should_not_exist(self, topic):
                    file_path = join(datetime.now().strftime('%Y/%m/%d'), 'crocodile3.jpg')
                    path = join(storage_path, file_path)
                    expect(topic).to_equal(200)
                    expect(exists(path)).to_be_true()

@Vows.batch
class UploadWithMinWidthAndHeight(BaseContext):
    def get_app(self):
        cfg = Config()
        cfg.ENABLE_ORIGINAL_PHOTO_UPLOAD = True
        cfg.ALLOW_ORIGINAL_PHOTO_PUTTING = True
        cfg.ORIGINAL_PHOTO_STORAGE = 'thumbor.storages.file_storage'
        cfg.FILE_STORAGE_ROOT_PATH = storage_path
        cfg.MIN_WIDTH = 40
        cfg.MIN_HEIGHT = 40

        importer = Importer(cfg)
        importer.import_modules()
        ctx = Context(None, cfg, importer)
        application = ThumborServiceApp(ctx)
        return application

    class WhenPuttingTooSmallImage(BaseContext):
        def topic(self):
            with open(crocodile_file_path, 'r') as croc:
                image = ('media', u'crocodile9999.jpg', croc.read())
            response = self.post_files('put', '/upload', {}, (image, ))
            return (response.code, response.body)

        def should_be_an_error(self, topic):
             expect(topic[0]).to_equal(412)

    class WhenPostingTooSmallImage(BaseContext):
        def topic(self):
            with open(crocodile_file_path, 'r') as croc:
                image = ('media', u'crocodile9999.jpg', croc.read())
            response = self.post_files('post', '/upload', {}, (image, ))
            return (response.code, response.body)

        def should_be_an_error(self, topic):
             expect(topic[0]).to_equal(412)

@Vows.batch
class UploadWithMaxSize(BaseContext):
    def get_app(self):
        cfg = Config()
        cfg.ENABLE_ORIGINAL_PHOTO_UPLOAD = True
        cfg.ALLOW_ORIGINAL_PHOTO_PUTTING = True
        cfg.ORIGINAL_PHOTO_STORAGE = 'thumbor.storages.file_storage'
        cfg.FILE_STORAGE_ROOT_PATH = storage_path
        cfg.MAX_SIZE = 40000

        importer = Importer(cfg)
        importer.import_modules()
        ctx = Context(None, cfg, importer)
        application = ThumborServiceApp(ctx)
        return application

    class WhenPuttingTooBigFile(BaseContext):
        def topic(self):
            with open(oversized_file_path, 'r') as croc:
                image = ('media', u'oversized9999.jpg', croc.read())
            response = self.post_files('put', '/upload', {}, (image, ))
            return (response.code, response.body)

        def should_be_an_error(self, topic):
             expect(topic[0]).to_equal(412)

    class WhenPostingTooBigFile(BaseContext):
        def topic(self):
            with open(oversized_file_path, 'r') as croc:
                image = ('media', u'oversized9999.jpg', croc.read())
            response = self.post_files('post', '/upload', {}, (image, ))
            return (response.code, response.body)

        def should_be_an_error(self, topic):
             expect(topic[0]).to_equal(412)
