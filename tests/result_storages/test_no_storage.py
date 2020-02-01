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
from thumbor.config import Config
from thumbor.context import Context, RequestParameters
from thumbor.result_storages.no_storage import Storage as NoStorage


class NoResultStorageTestCase(TestCase):
    def get_context(self):
        cfg = Config()
        ctx = Context(None, cfg, None)
        ctx.request = RequestParameters(url="image.jpg")
        self.context = ctx
        return ctx

    @gen_test
    async def test_result_has_no_image(self):
        fs = NoStorage(self.context)
        result = await fs.get()
        expect(result).to_be_none

    @gen_test
    async def test_can_put_image(self):
        fs = NoStorage(self.context)
        result = await fs.put(100)
        expect(result).to_equal("")
