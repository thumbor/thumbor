#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from os.path import abspath, dirname, join

from preggy import expect
from tornado.testing import gen_test

from tests.base import TestCase
from thumbor.storages.no_storage import Storage as NoStorage


class NoStorageTestCase(TestCase):
    def get_image_url(self, image):
        return f"s.glbimg.com/some/{image}"

    def get_image_path(self, image):
        return join(abspath(dirname(__file__)), image)

    def get_image_bytes(self, image):
        ipath = self.get_image_path(image)
        with open(ipath, "rb") as img:
            return img.read()

    @gen_test
    async def test_store_image_should_be_null(self):
        iurl = self.get_image_url("source.jpg")
        storage = NoStorage(None)
        stored = await storage.get(iurl)
        expect(stored).to_be_null()

    @gen_test
    async def test_store_knows_no_image(self):
        iurl = self.get_image_url("source.jpg")
        storage = NoStorage(None)
        exists = await storage.exists(iurl)
        expect(exists).to_be_false()

    @gen_test
    async def test_removes_image_should_be_null(self):
        iurl = self.get_image_url("source.jpg")
        storage = NoStorage(None)
        removed = await storage.remove(iurl)
        expect(removed).to_be_null()

    @gen_test
    async def test_stores_crypto_should_be_null(self):
        iurl = self.get_image_url("source.jpg")
        storage = NoStorage(None)
        await storage.put_crypto(iurl)
        got_crypto = await storage.get_crypto(iurl)
        expect(got_crypto).to_be_null()

    @gen_test
    async def test_detector_data_should_be_null(self):
        iurl = self.get_image_url("source.jpg")
        storage = NoStorage(None)
        await storage.put_detector_data(iurl, "some data")
        data = await storage.get_detector_data(iurl)
        expect(data).to_be_null()
