#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import sys
from os.path import join, abspath, dirname

sys.path.append(abspath(join(dirname(__file__), '..')))

from tornado.testing import AsyncHTTPTestCase
from thumbor.app import ThumborServiceApp


class ThumborServiceTest(AsyncHTTPTestCase):

    def get_app(self):
        return ThumborServiceApp()

    def test_app_exists_and_is_instanceof_thumborserviceapp(self):
        assert isinstance(self._app, ThumborServiceApp), 'App does not exist or is not instance of the ThumborServiceApp class'
