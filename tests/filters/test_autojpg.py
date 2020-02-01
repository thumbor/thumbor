#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license

from preggy import expect
from tornado.testing import gen_test

from tests.base import FilterTestCase


class AutoJPGFilterTestCase(FilterTestCase):
    @gen_test
    async def test_autojpg_filter_sets_param_to_true(self):
        fltr = self.get_filter("thumbor.filters.autojpg", "autojpg()")
        expect(self.context.request.auto_png_to_jpg).to_equal(None)

        await fltr.run()

        expect(self.context.request.auto_png_to_jpg).to_equal(True)

    @gen_test
    async def test_autojpg_filter_sets_param_to_false(self):
        fltr = self.get_filter("thumbor.filters.autojpg", "autojpg(False)")
        expect(self.context.request.auto_png_to_jpg).to_equal(None)

        await fltr.run()

        expect(self.context.request.auto_png_to_jpg).to_equal(False)
