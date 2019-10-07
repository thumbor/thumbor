#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect

from thumbor.config import Config
from thumbor.context import Context
from thumbor.importer import Importer
from tests.base import TestCase


class HealthcheckHandlerTestCase(TestCase):
    def test_can_get_healthcheck(self):
        response = self.fetch('/healthcheck')
        expect(response.code).to_equal(200)
        expect(response.body).to_equal("WORKING")
        expect(response.headers.get('Cache-Control')).to_equal('no-cache')

    def test_can_head_healthcheck(self):
        response = self.fetch('/healthcheck', method='HEAD')
        expect(response.code).to_equal(200)
        expect(response.headers.get('Cache-Control')).to_equal('no-cache')


# Same test, but configured for the root URL
class HealthcheckOnRootTestCase(TestCase):
    def get_context(self):
        cfg = Config()
        cfg.HEALTHCHECK_ROUTE = '/'

        importer = Importer(cfg)
        importer.import_modules()

        return Context(None, cfg, importer)

    def test_can_get_healthcheck(self):
        response = self.fetch('/')
        expect(response.code).to_equal(200)
        expect(response.body).to_equal("WORKING")

    def test_can_head_healthcheck(self):
        response = self.fetch('/', method='HEAD')
        expect(response.code).to_equal(200)
