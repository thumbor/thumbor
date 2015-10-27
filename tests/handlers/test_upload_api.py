#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from shutil import rmtree
import tempfile

from preggy import expect

from thumbor.config import Config
from thumbor.importer import Importer
from thumbor.context import Context
from tests.base import TestCase
from tests.fixtures.images import valid_image, valid_image_path


class UploadAPITestCase(TestCase):
    @classmethod
    def setUpClass(cls, *args, **kw):
        cls.root_path = tempfile.mkdtemp()
        cls.base_uri = "/image"

    @classmethod
    def tearDownClass(cls, *args, **kw):
        rmtree(cls.root_path)

    @property
    def upload_storage(self):
        return self.context.modules.upload_photo_storage

    def get_path_from_location(self, location):
        return "/".join(
            location.lstrip('/').rstrip('/').split('/')[1:-1]
        )

    def get_context(self):
        self.default_filename = 'image'

        cfg = Config()
        cfg.UPLOAD_ENABLED = True
        cfg.UPLOAD_PHOTO_STORAGE = 'thumbor.storages.file_storage'
        cfg.FILE_STORAGE_ROOT_PATH = self.root_path
        cfg.UPLOAD_DELETE_ALLOWED = False
        cfg.UPLOAD_PUT_ALLOWED = False
        cfg.UPLOAD_DEFAULT_FILENAME = self.default_filename

        importer = Importer(cfg)
        importer.import_modules()

        return Context(None, cfg, importer)

    def test_can_post_image_with_content_type(self):
        filename = 'new_image_with_a_filename.jpg'
        response = self.post(self.base_uri, {'Content-Type': 'image/jpeg', 'Slug': filename}, valid_image())

        expect(response.code).to_equal(201)

        expect(response.headers).to_include('Location')
        expect(response.headers['Location']).to_match(self.base_uri + r'/[^\/]{32}/' + filename)

        expected_path = self.get_path_from_location(response.headers['Location'])
        expected_path = self.upload_storage.path_on_filesystem(expected_path)
        expect(expected_path).to_exist()
        expect(expected_path).to_be_the_same_as(valid_image_path)

    def test_can_post_image_with_charset(self):
        filename = self.default_filename + '.jpg'
        response = self.post(self.base_uri, {'Content-Type': 'image/jpeg;charset=UTF-8'}, valid_image())

        expect(response.code).to_equal(201)

        expect(response.headers).to_include('Location')
        expect(response.headers['Location']).to_match(self.base_uri + r'/[^\/]{32}/' + filename)

        expected_path = self.get_path_from_location(response.headers['Location'])
        expected_path = self.upload_storage.path_on_filesystem(expected_path)
        expect(expected_path).to_exist()
        expect(expected_path).to_be_the_same_as(valid_image_path)

    def test_can_post_image_with_unknown_charset(self):
        filename = self.default_filename + '.jpg'
        response = self.post(self.base_uri, {'Content-Type': 'image/thisIsAUnknwonOrBadlyFormedCHarset'}, valid_image())

        expect(response.code).to_equal(201)

        expect(response.headers).to_include('Location')
        expect(response.headers['Location']).to_match(self.base_uri + r'/[^\/]{32}/' + filename)

        expected_path = self.get_path_from_location(response.headers['Location'])
        expected_path = self.upload_storage.path_on_filesystem(expected_path)
        expect(expected_path).to_exist()
        expect(expected_path).to_be_the_same_as(valid_image_path)

    def test_can_post_image_without_filename(self):
        filename = self.default_filename + '.jpg'
        response = self.post(self.base_uri, {'Content-Type': 'image/jpeg'}, valid_image())

        expect(response.code).to_equal(201)

        expect(response.headers).to_include('Location')
        expect(response.headers['Location']).to_match(self.base_uri + r'/[^\/]{32}/' + filename)

        expected_path = self.get_path_from_location(response.headers['Location'])
        expected_path = self.upload_storage.path_on_filesystem(expected_path)
        expect(expected_path).to_exist()
        expect(expected_path).to_be_the_same_as(valid_image_path)

    def test_can_post_from_html_form(self):
        filename = 'crocodile2.jpg'
        image = ('media', filename, valid_image())
        response = self.post_files(self.base_uri, {'Slug': 'another_filename.jpg'}, (image, ))

        expect(response.code).to_equal(201)

        expect(response.headers).to_include('Location')
        expect(response.headers['Location']).to_match(self.base_uri + r'/[^\/]{32}/' + filename)

        expected_path = self.get_path_from_location(response.headers['Location'])
        expected_path = self.upload_storage.path_on_filesystem(expected_path)
        expect(expected_path).to_exist()
        expect(expected_path).to_be_the_same_as(valid_image_path)
