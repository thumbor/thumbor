#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect

from thumbor.handlers.image_resource import ImageResourceHandler
from thumbor.handlers.upload import ImageUploadHandler
from thumbor.routers.base import Route
from thumbor.routers.upload import UploadRouter
from thumbor.testing import TestCase


class UploadRouterTestCase(TestCase):
    def test_can_get_routes(self):
        ctx = self.get_context()
        ctx.config.UPLOAD_ENABLED = True
        routes = UploadRouter(ctx).get_routes()

        expect(routes).not_to_be_null()
        expect(routes).to_length(2)
        expect(routes[0]).to_be_instance_of(Route)
        expect(routes[0].url).to_equal(r"/image")
        expect(routes[0].handler).to_equal(ImageUploadHandler)
        expect(routes[0].initialize).to_equal({"context": ctx})
        expect(routes[1]).to_be_instance_of(Route)
        expect(routes[1].url).to_equal(r"/image/(.*)")
        expect(routes[1].handler).to_equal(ImageResourceHandler)
        expect(routes[1].initialize).to_equal({"context": ctx})

    def test_can_disable_upload(self):
        ctx = self.get_context()
        ctx.config.UPLOAD_ENABLED = False
        routes = UploadRouter(ctx).get_routes()

        expect(routes).not_to_be_null()
        expect(routes).to_be_empty()
