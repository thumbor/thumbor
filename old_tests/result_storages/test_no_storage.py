#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect

from thumbor.context import Context, RequestParameters
from thumbor.config import Config
from thumbor.result_storages.no_storage import Storage as NoStorage
from tests.base import TestCase


class NoResultStorageTestCase(TestCase):
    def get_context(self):
        cfg = Config()
        ctx = Context(None, cfg, None)
        ctx.request = RequestParameters(url='image.jpg')
        self.context = ctx
        return ctx

    def test_result_has_no_image(self):
        fs = NoStorage(self.context)
        result = fs.get(callback=lambda a: a)
        expect(result).to_be_none

    def test_can_put_image(self):
        fs = NoStorage(self.context)
        result = fs.put(100)
        expect(result).to_equal('')
