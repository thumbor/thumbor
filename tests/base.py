#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com


from thumbor.app import ThumborServiceApp
from thumbor.context import Context
from thumbor.config import Config

from tornado.testing import AsyncHTTPTestCase


class TestCase(AsyncHTTPTestCase):
    def get_app(self):
        return ThumborServiceApp(self.get_context())

    def get_context(self):
        return Context(None, Config(), None)
