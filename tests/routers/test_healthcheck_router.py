#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect

from thumbor.handlers.healthcheck import HealthcheckHandler
from thumbor.routers.base import Route
from thumbor.routers.healthcheck import HealthcheckRouter
from thumbor.testing import TestCase


class HealthcheckRouterTestCase(TestCase):
    def test_can_get_routes(self):
        routes = HealthcheckRouter(self.context).get_routes()

        expect(routes).not_to_be_null()
        expect(routes).to_length(1)
        expect(routes[0]).to_be_instance_of(Route)
        expect(routes[0].url).to_equal(r"/healthcheck/?")
        expect(routes[0].handler).to_equal(HealthcheckHandler)

    def test_can_get_routes_with_custom_url(self):
        ctx = self.get_context()
        ctx.config.HEALTHCHECK_ROUTE = "/health"
        routes = HealthcheckRouter(ctx).get_routes()

        expect(routes).not_to_be_null()
        expect(routes).to_length(1)
        expect(routes[0]).to_be_instance_of(Route)
        expect(routes[0].url).to_equal("/health")
        expect(routes[0].handler).to_equal(HealthcheckHandler)
