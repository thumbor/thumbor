#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect
from tornado.testing import gen_test

from tests.base import TestCase
from thumbor.context import RequestParameters
from thumbor.result_storages.no_storage import Storage as NoStorage


class NoResultStorageTestCase(TestCase):
    def get_context(self):
        ctx = super().get_context()
        ctx.request = RequestParameters(url="image.jpg")
        self.context = ctx
        return ctx

    @gen_test
    async def test_result_has_no_image(self):
        no_storage = NoStorage(self.context)
        result = await no_storage.get()
        expect(result).to_be_null()

    @gen_test
    async def test_can_put_image(self):
        no_storage = NoStorage(self.context)
        result = await no_storage.put(100)
        expect(result).to_equal("")
