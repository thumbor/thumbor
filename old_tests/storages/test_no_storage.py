#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from os.path import join, abspath, dirname
from preggy import expect

from thumbor.context import Context
from thumbor.config import Config
from thumbor.storages.no_storage import Storage as NoStorage
from tests.base import TestCase


class NoStorageTestCase(TestCase):
    def get_context(self):
        cfg = Config()
        return Context(None, cfg, None)

    def get_image_url(self, image):
        return 's.glbimg.com/some/{0}'.format(image)

    def get_image_path(self, image):
        return join(abspath(dirname(__file__)), image)

    def get_image_bytes(self, image):
        ipath = self.get_image_path(image)
        with open(ipath, 'r') as img:
            return img.read()

    def test_store_image_should_be_null(self):
        iurl = self.get_image_url('source.jpg')
        storage = NoStorage(None)
        stored = storage.get(iurl)
        expect(stored.result()).to_be_null()

    def test_store_knows_no_image(self):
        iurl = self.get_image_url('source.jpg')
        storage = NoStorage(None)
        exists = storage.exists(iurl)
        expect(exists.result()).to_be_false()

    def test_removes_image_should_be_null(self):
        iurl = self.get_image_url('source.jpg')
        storage = NoStorage(None)
        removed = storage.remove(iurl)
        expect(removed).to_be_null()

    def test_stores_crypto_should_be_null(self):
        iurl = self.get_image_url('source.jpg')
        storage = NoStorage(None)
        storage.put_crypto(iurl)
        got_crypto = storage.get_crypto(iurl)
        expect(got_crypto.result()).to_be_null()

    def test_detector_data_should_be_null(self):
        iurl = self.get_image_url('source.jpg')
        storage = NoStorage(None)
        storage.put_detector_data(iurl, "some data")
        data = storage.get_detector_data(iurl)
        expect(data.result()).to_be_null()
