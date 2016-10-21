#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect

from tests.base import TestCase


class HealthcheckHandlerTestCase(TestCase):
    def test_can_get_healthcheck(self):
        response = self.fetch('/healthcheck')
        expect(response.code).to_equal(200)
        expect(response.body).to_equal("WORKING")

    def test_can_head_healthcheck(self):
        response = self.fetch('/healthcheck', method='HEAD')
        expect(response.code).to_equal(200)
