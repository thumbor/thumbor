#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from os.path import abspath, join, dirname, exists
from shutil import rmtree

from preggy import expect

from thumbor.config import Config
from thumbor.context import Context
from thumbor.importer import Importer
from tests.base import TestCase


class BlacklistHandlerTestCase(TestCase):
    def get_context(self):
        file_storage_root_path = '/tmp/thumbor/storage'
        if exists(file_storage_root_path):
            rmtree(file_storage_root_path)

        cfg = Config()
        cfg.USE_BLACKLIST = True
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = abspath(join(dirname(__file__), '../fixtures/images/'))
        cfg.STORAGE = 'thumbor.storages.file_storage'
        cfg.FILE_STORAGE_ROOT_PATH = file_storage_root_path
        importer = Importer(cfg)
        importer.import_modules()
        return Context(None, cfg, importer)

    def test_can_get_blacklist(self):
        response = self.fetch('/blacklist')
        expect(response.code).to_equal(200)
        expect(response.body).to_equal("")

    def test_can_put_object_to_blacklist(self):
        response = self.fetch('/blacklist?blocked.jpg', method='PUT', body='')
        expect(response.code).to_equal(200)
        expect(response.body).to_equal("")

    def test_can_read_updated_blacklist(self):
        self.fetch('/blacklist?blocked.jpg', method='PUT', body='')
        response = self.fetch('/blacklist')
        expect(response.code).to_equal(200)
        expect("blocked.jpg\n" in response.body).to_equal(True)

    def test_cant_get_blacklisted_image(self):
        response = self.fetch('/unsafe/image.jpg')
        expect(response.code).to_equal(200)
        self.fetch('/blacklist?image.jpg', method='PUT', body='')
        response = self.fetch('/unsafe/image.jpg')
        expect(response.code).to_equal(400)
