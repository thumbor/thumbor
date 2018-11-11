#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from mock import MagicMock
from preggy import expect
from tornado.concurrent import Future

from tests.unit import BaseTestCase
from thumbor.blueprints.loaders.https import HttpsLoader


class NormalizeUrlTestCase(BaseTestCase):
    def test_should_normalize_url(self):
        """[HttpsLoader._normalize_url] Tests it adds https"""
        loader = HttpsLoader()

        for url in ["https://some.url", "some.url"]:
            expect(loader._normalize_url(url)).to_equal("https://some.url")
