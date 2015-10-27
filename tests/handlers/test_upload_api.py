#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from shutil import rmtree
import tempfile
from os.path import exists

from preggy import expect, create_assertions

from thumbor.config import Config
from thumbor.importer import Importer
from thumbor.context import Context
from tests.base import TestCase
from tests.fixtures.images import valid_image, valid_image_path


@create_assertions
def to_exist(topic):
    return exists(topic)


@create_assertions
def to_be_the_same_as(topic, expected):
    if not exists(topic):
        raise AssertionError("File at %s does not exist" % topic)
    if not exists(expected):
        raise AssertionError("File at %s does not exist" % expected)

    with open(topic, 'r') as source:
        topic_contents = source.read()

    with open(expected, 'r') as source:
        expected_contents = source.read()

    return topic_contents == expected_contents


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
            location.replace(self.base_uri, '').split('/')[:-1]
        ).rstrip('/').lstrip('/')

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

    def test_can_post_image(self):
        filename = 'new_image_with_a_filename.jpg'
        response = self.post(self.base_uri, {'Content-Type': 'image/jpeg', 'Slug': filename}, valid_image())

        expect(response.code).to_equal(201)

        expect(response.headers).to_include('Location')
        expect(response.headers['Location']).to_match(self.base_uri + r'/[^\/]{32}/' + filename)

        expected_path = self.get_path_from_location(response.headers['Location'])
        expected_path = self.upload_storage.path_on_filesystem(expected_path)
        expect(expected_path).to_exist()
        expect(expected_path).to_be_the_same_as(valid_image_path)
