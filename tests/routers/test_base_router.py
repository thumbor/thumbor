#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from mock import Mock
from preggy import expect

from thumbor.routers.base import Route
from thumbor.testing import TestCase


class BaseRouterTestCase(TestCase):
    @staticmethod
    def test_can_create_route():
        url = "/qwe"
        controller = Mock()
        init = {"qwe": 123}
        route = Route(url, controller, init)
        expect(route).not_to_be_null()
        expect(route.url).to_equal(url)
        expect(route.handler).to_equal(controller)
        expect(route.initialize).to_equal(init)
