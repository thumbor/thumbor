#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import abspath, join, dirname, exists
import re

from pyvows import Vows, expect
from tornado_pyvows.context import TornadoHTTPContext

from shutil import rmtree
from thumbor.app import ThumborServiceApp
from thumbor.config import Config
from thumbor.importer import Importer
from thumbor.context import Context

import urllib
import hashlib
import mimetypes


file_storage_root_path = '/tmp/thumbor-vows/storage'
file_path = ''


##
# Images used for tests :
#   - valid image      : JPEG 620x465, 69.88 KB
#   - too small image  : JPEG 20x20, 822 B
#   - too weight image : JPEG 300x400, 85.32 KB
##
def valid_image():
    path = abspath(join(dirname(__file__), 'fixtures/alabama1_ap620é.jpg'))
    with open(path, 'r') as stream:
        body = stream.read()
    return body


def too_small_image():
    path = abspath(join(dirname(__file__), 'crocodile.jpg'))
    with open(path, 'r') as stream:
        body = stream.read()
    return body


def too_weight_image():
    path = abspath(join(dirname(__file__), 'fixtures/conselheira_tutelar.jpg'))
    with open(path, 'r') as stream:
        body = stream.read()
    return body


if exists(file_storage_root_path):
    rmtree(file_storage_root_path)


##
# Path on file system (filestorage)
##
def path_on_filesystem(path):
    digest = hashlib.sha1(path).hexdigest()
    return join(file_storage_root_path.rstrip('/'), digest[:2] + '/' + digest[2:])


def encode_multipart_formdata(fields, files):
    BOUNDARY = 'thumborUploadFormBoundary'
    CRLF = '\r\n'
    L = []
    for key, value in fields.items():
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % mimetypes.guess_type(filename)[0] or 'application/octet-stream')
        L.append('')
        L.append(value)
    L.append('')
    L.append('')
    L.append('--' + BOUNDARY + '--')
    body = CRLF.join([str(item) for item in L])
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body


##
# Image Context defining post / put / delete / get
##
class ImageContext(TornadoHTTPContext):
    def __init__(self, *args, **kw):
        super(ImageContext, self).__init__(*args, **kw)
        self.ignore('get', 'post', 'put', 'delete', 'post_files')
        self.base_uri = "/image"

    def get(self, path, headers):
        return self.fetch(path,
                          method='GET',
                          body=urllib.urlencode({}, doseq=True),
                          headers=headers,
                          allow_nonstandard_methods=True)

    def post(self, path, headers, body):
        return self.fetch(path,
                          method='POST',
                          body=body,
                          headers=headers,
                          allow_nonstandard_methods=True)

    def put(self, path, headers, body):
        return self.fetch(path,
                          method='PUT',
                          body=body,
                          headers=headers,
                          allow_nonstandard_methods=True)

    def delete(self, path, headers):
        return self.fetch(path,
                          method='DELETE',
                          body=urllib.urlencode({}, doseq=True),
                          headers=headers,
                          allow_nonstandard_methods=True)

    def post_files(self, path, data={}, files=[]):
        multipart_data = encode_multipart_formdata(data, files)

        return self.fetch(path,
                          method='POST',
                          body=multipart_data[1],
                          headers={
                              'Content-Type': multipart_data[0]
                          },
                          allow_nonstandard_methods=True)


##
# Upload new images with POST method
##
@Vows.batch
class PostingANewImage(ImageContext):
    def get_app(self):
        self.default_filename = 'image'

        cfg = Config()
        cfg.UPLOAD_ENABLED = True
        cfg.UPLOAD_PHOTO_STORAGE = 'thumbor.storages.file_storage'
        cfg.FILE_STORAGE_ROOT_PATH = file_storage_root_path
        cfg.UPLOAD_DELETE_ALLOWED = False
        cfg.UPLOAD_PUT_ALLOWED = False
        cfg.UPLOAD_DEFAULT_FILENAME = self.default_filename

        importer = Importer(cfg)
        importer.import_modules()

        ctx = Context(None, cfg, importer)
        application = ThumborServiceApp(ctx)
        return application

    ##
    # Posting a new image with a filename through the REST API
    ##
    class WhenPostingANewImageWithAFilename(ImageContext):
        def topic(self):
            self.filename = 'new_image_with_a_filename.jpg'
            response = self.post(self.base_uri, {'Content-Type': 'image/jpeg', 'Slug': self.filename}, valid_image())
            return response

        class HttpStatusCode(ImageContext):
            def topic(self, response):
                return response.code

            def should_be_201_created(self, topic):
                expect(topic).to_equal(201)

        class HttpHeaders(ImageContext):
            def topic(self, response):
                return response.headers

            def should_contain_a_location_header_containing_the_filename(self, headers):
                expect(headers).to_include('Location')
                expect(headers['Location']).to_match(self.base_uri + r'/[^\/]{32}/' + self.filename)

        class Image(ImageContext):
            def topic(self, response):
                return re.compile(self.base_uri + r'/([^\/]{32})/' + self.filename).search(
                    response.headers['Location']).group(1)

            def should_be_store_at_right_path(self, topic):
                path = path_on_filesystem(topic)
                expect(exists(path)).to_be_true()

    ##
    # Posting a new image without filename through the REST API
    ##
    class WhenPostingANewImageWithoutFilename(ImageContext):
        def topic(self):
            self.filename = self.default_filename + '.jpg'
            response = self.post(self.base_uri, {'Content-Type': 'image/jpeg'}, valid_image())
            return response

        class HttpStatusCode(ImageContext):
            def topic(self, response):
                return response.code

            def should_be_201_created(self, topic):
                expect(topic).to_equal(201)

        class HttpHeaders(ImageContext):
            def topic(self, response):
                return response.headers

            def should_contain_a_location_header_containing_the_filename(self, headers):
                expect(headers).to_include('Location')
                expect(headers['Location']).to_match(self.base_uri + r'/[^\/]{32}/' + self.filename)

        class Image(ImageContext):
            def topic(self, response):
                return re.compile(self.base_uri + r'/([^\/]{32})/' + self.filename).search(
                    response.headers['Location']).group(1)

            def should_be_store_at_right_path(self, topic):
                path = path_on_filesystem(topic)
                expect(exists(path)).to_be_true()

    ##
    # Posting a new image through an HTML Form (multipart/form-data)
    ##
    class WhenPostingAValidImageThroughAnHtmlForm(ImageContext):
        def topic(self):
            self.filename = 'crocodile2.jpg'
            image = ('media', self.filename, valid_image())
            response = self.post_files(self.base_uri, {'Slug': 'another_filename.jpg'}, (image, ))
            return response

        class HttpStatusCode(ImageContext):
            def topic(self, response):
                return response.code

            def should_be_201_created(self, topic):
                expect(topic).to_equal(201)

        class HttpHeaders(ImageContext):
            def topic(self, response):
                return response.headers

            def should_contain_a_location_header_containing_the_filename(self, headers):
                expect(headers).to_include('Location')
                expect(headers['Location']).to_match(self.base_uri + r'/[^\/]{32}/' + self.filename)

        class Image(ImageContext):
            def topic(self, response):
                return re.compile(self.base_uri + r'/([^\/]{32})/' + self.filename).search(
                    response.headers['Location']).group(1)

            def should_be_store_at_right_path(self, topic):
                path = path_on_filesystem(topic)
                expect(exists(path)).to_be_true()


##
# Modifying an image
##
@Vows.batch
class ModifyingAnImage(ImageContext):

    def get_app(self):
        self.default_filename = 'image'

        cfg = Config()
        cfg.UPLOAD_ENABLED = True
        cfg.UPLOAD_PHOTO_STORAGE = 'thumbor.storages.file_storage'
        cfg.FILE_STORAGE_ROOT_PATH = file_storage_root_path
        cfg.UPLOAD_DELETE_ALLOWED = False
        cfg.UPLOAD_PUT_ALLOWED = True
        cfg.UPLOAD_DEFAULT_FILENAME = self.default_filename

        importer = Importer(cfg)
        importer.import_modules()

        ctx = Context(None, cfg, importer)
        application = ThumborServiceApp(ctx)
        return application

    ##
    # Modifying an image
    ##
    class WhenModifyingAnExistingImage(ImageContext):
        def topic(self):
            self.filename = self.default_filename + '.jpg'
            response = self.post(self.base_uri, {'Content-Type': 'image/jpeg'}, valid_image())
            self.location = response.headers['Location']
            response = self.put(self.location, {'Content-Type': 'image/jpeg'}, valid_image())
            return response

        class HttpStatusCode(ImageContext):
            def topic(self, response):
                return response.code

            def should_be_204_no_content(self, topic):
                expect(topic).to_equal(204)

        class Image(ImageContext):
            def topic(self, response):
                return re.compile(self.base_uri + r'/([^\/]{32})/' + self.filename).search(self.location).group(1)

            def should_be_store_at_right_path(self, topic):
                # Only file with uuid should be store
                id_should_exists = re.compile(self.base_uri + r'/([^\/]{32})/' + self.filename).search(self.location).group(1)
                expect(exists(path_on_filesystem(id_should_exists))).to_be_true()

                id_shouldnt_exists = re.compile(self.base_uri + r'/(.*)').search(self.location).group(1)
                expect(exists(path_on_filesystem(id_shouldnt_exists))).to_be_false()


##
# Delete image with DELETE method
##
@Vows.batch
class DeletingAnImage(ImageContext):
    def get_app(self):
        self.default_filename = 'image'

        cfg = Config()
        cfg.UPLOAD_ENABLED = True
        cfg.UPLOAD_PHOTO_STORAGE = 'thumbor.storages.file_storage'
        cfg.FILE_STORAGE_ROOT_PATH = file_storage_root_path
        cfg.UPLOAD_DELETE_ALLOWED = True
        cfg.UPLOAD_PUT_ALLOWED = False
        cfg.UPLOAD_DEFAULT_FILENAME = self.default_filename

        importer = Importer(cfg)
        importer.import_modules()

        ctx = Context(None, cfg, importer)
        application = ThumborServiceApp(ctx)
        return application

    ##
    # Deleting  an existing image
    ##
    class WhenDeletingAnExistingImage(ImageContext):
        def topic(self):
            self.filename = self.default_filename + '.jpg'
            response = self.post(self.base_uri, {'Content-Type': 'image/jpeg'}, valid_image())
            self.location = response.headers['Location']
            response = self.delete(self.location, {})
            return response

        class HttpStatusCode(ImageContext):
            def topic(self, response):
                return response.code

            def should_be_204_no_content(self, topic):
                expect(topic).to_equal(204)

        class Image(ImageContext):
            def topic(self, response):
                return response

            def should_be_deleted_from_storage(self, topic):
                # Only file with uuid should be store
                id_shouldnt_exists = re.compile(self.base_uri + r'/([^\/]{32})/' + self.filename).search(self.location).group(1)
                expect(exists(path_on_filesystem(id_shouldnt_exists))).to_be_false()

    ##
    # Deleting  an unknown image
    ##
    class WhenDeletingAnUnknownImage(ImageContext):
        def topic(self):
            self.uri = self.base_uri + '/an/unknown/image'
            response = self.delete(self.uri, {})
            return response

        class HttpStatusCode(ImageContext):
            def topic(self, response):
                return response.code

            def should_be_404_not_found(self, topic):
                expect(topic).to_equal(404)


##
# Retrieving image
##
@Vows.batch
class RetrievingAnImage(ImageContext):
    def get_app(self):
        self.default_filename = 'image'

        cfg = Config()
        cfg.UPLOAD_ENABLED = True
        cfg.UPLOAD_PHOTO_STORAGE = 'thumbor.storages.file_storage'
        cfg.FILE_STORAGE_ROOT_PATH = file_storage_root_path
        cfg.UPLOAD_DELETE_ALLOWED = True
        cfg.UPLOAD_PUT_ALLOWED = False
        cfg.UPLOAD_DEFAULT_FILENAME = self.default_filename

        importer = Importer(cfg)
        importer.import_modules()

        ctx = Context(None, cfg, importer)
        application = ThumborServiceApp(ctx)
        return application

    class WhenRetrievingAnExistingImage(ImageContext):
        def topic(self):
            response = self.post(self.base_uri, {'Content-Type': 'image/jpeg'}, valid_image())
            self.location = response.headers['Location']
            response = self.get(self.location, {'Accept': 'image/jpeg'})
            return response

        class HttpStatusCode(ImageContext):
            def topic(self, response):
                return response.code

            def should_be_200_ok(self, topic):
                expect(topic).to_equal(200)

        class Body(ImageContext):
            def topic(self, response):
                return response.body

            def should_be_the_expected_image(self, topic):
                expect(topic).to_equal(valid_image())

    class WhenRetrievingAnUnknownImage(ImageContext):
        def topic(self):
            self.uri = self.base_uri + '/an/unknown/image'
            response = self.get(self.uri, {'Accept': 'image/jpeg'})
            return response

        class HttpStatusCode(ImageContext):
            def topic(self, response):
                return response.code

            def should_be_404_not_found(self, topic):
                expect(topic).to_equal(404)


##
# Validation :
#   - Invalid image
#   - Size constraints
#   - Weight constraints
##
@Vows.batch
class Validation(ImageContext):

    def get_app(self):
        self.default_filename = 'image'

        cfg = Config()
        cfg.UPLOAD_ENABLED = True
        cfg.UPLOAD_PUT_ALLOWED = True
        cfg.UPLOAD_PHOTO_STORAGE = 'thumbor.storages.file_storage'
        cfg.FILE_STORAGE_ROOT_PATH = file_storage_root_path
        cfg.UPLOAD_DEFAULT_FILENAME = self.default_filename
        cfg.MIN_WIDTH = 40
        cfg.MIN_HEIGHT = 40
        cfg.UPLOAD_MAX_SIZE = 72000

        importer = Importer(cfg)
        importer.import_modules()
        ctx = Context(None, cfg, importer)
        application = ThumborServiceApp(ctx)
        return application

    ##
    # Invalid Image
    ##
    class InvalidImage(ImageContext):

        ##
        # Posting an invalid image
        ##
        class WhenPostingAnInvalidImage(ImageContext):
            def topic(self):
                response = self.post(self.base_uri, {'Content-Type': 'image/jpeg'}, 'invalid image')
                return response

            class HttpStatusCode(ImageContext):
                def topic(self, response):
                    return response.code

                def should_be_415_media_type_not_supported(self, topic):
                    expect(topic).to_equal(415)

        ##
        # Posting an invalid image through an html form (multipart/form-data)
        ##
        class WhenPostingAnInvalidImageThroughAnHtmlForm(ImageContext):
            def topic(self):
                image = ('media', u'crocodile9999.jpg', 'invalid image')
                response = self.post_files(self.base_uri, {}, (image, ))
                return response

            class HttpStatusCode(ImageContext):
                def topic(self, response):
                    return response.code

                def should_be_415_media_type_not_supported(self, topic):
                        expect(topic).to_equal(415)

        ##
        # Modifying an existing image by an invalid image
        ##
        class WhenModifyingAnExistingImageByAnInvalidImage(ImageContext):
            def topic(self):
                response = self.post(self.base_uri, {'Content-Type': 'image/jpeg'}, valid_image())
                self.location = response.headers['Location']
                response = self.put(self.location, {'Content-Type': 'image/jpeg'}, 'invalid image')
                return response

            class HttpStatusCode(ImageContext):
                def topic(self, response):
                    return response.code

                def should_be_415_media_type_not_supported(self, topic):
                    expect(topic).to_equal(415)

    ##
    # Size constraints
    ##
    class ImageSizeConstraints(ImageContext):

        ##
        # Posting a too small image
        ##
        class WhenPostingATooSmallImage(ImageContext):
            def topic(self):
                response = self.post(self.base_uri, {'Content-Type': 'image/jpeg'}, too_small_image())
                return response

            class HttpStatusCode(ImageContext):
                def topic(self, response):
                    return response.code

                def should_be_412_precondition_failed(self, topic):
                    expect(topic).to_equal(412)

        ##
        # Posting a too small image through an html form (multipart/form-data)
        ##
        class WhenPostingTooSmallImageThroughAnHtmlForm(ImageContext):
            def topic(self):
                image = ('media', u'crocodile9999.jpg', too_small_image())
                response = self.post_files(self.base_uri, {}, (image, ))
                return (response.code, response.body)

            def should_be_an_error(self, topic):
                expect(topic[0]).to_equal(412)

        ##
        # Modifying an existing image by a too small image
        ##
        class WhenModifyingAnExistingImageByATooSmallImage(ImageContext):
            def topic(self):
                response = self.post(self.base_uri, {'Content-Type': 'image/jpeg'}, valid_image())
                self.location = response.headers['Location']
                response = self.put(self.location, {'Content-Type': 'image/jpeg'}, too_small_image())
                return response

            class HttpStatusCode(ImageContext):
                def topic(self, response):
                    return response.code

                def should_be_412_precondition_failed(self, topic):
                    expect(topic).to_equal(412)

    ##
    # Weight constraints
    ##
    class WeightConstraints(ImageContext):

        ##
        # Posting a too weight image
        ##
        class WhenPostingATooWeightImage(ImageContext):
            def topic(self):
                response = self.post(self.base_uri, {'Content-Type': 'image/jpeg'}, too_weight_image())
                return response

            class HttpStatusCode(ImageContext):
                def topic(self, response):
                    return response.code

                def should_be_412_precondition_failed(self, topic):
                    expect(topic).to_equal(412)

        ##
        # Posting a too weight image through an html form (multipart/form-data)
        ##
        class WhenPostingATooWeightImageThroughAnHtmlForm(ImageContext):
            def topic(self):
                image = ('media', u'oversized9999.jpg', too_weight_image())
                response = self.post_files(self.base_uri, {}, (image, ))
                return (response.code, response.body)

            def should_be_an_error(self, topic):
                expect(topic[0]).to_equal(412)

        ##
        # Modifying an existing image by a too weight image
        ##
        class WhenModifyingAnExistingImageByATooWeightImage(ImageContext):
            def topic(self):
                response = self.post(self.base_uri, {'Content-Type': 'image/jpeg'}, valid_image())
                self.location = response.headers['Location']
                response = self.put(self.location, {'Content-Type': 'image/jpeg'}, too_weight_image())
                return response

            class HttpStatusCode(ImageContext):
                def topic(self, response):
                    return response.code

                def should_be_412_precondition_failed(self, topic):
                    expect(topic).to_equal(412)
