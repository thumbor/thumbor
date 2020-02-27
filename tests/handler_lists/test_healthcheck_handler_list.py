#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect

import thumbor.handler_lists.healthcheck as handler_list
from thumbor.handlers.healthcheck import HealthcheckHandler
from thumbor.testing import TestCase


class HealthcheckHandlerListTestCase(TestCase):
    def test_can_get_handlers(self):
        handlers = handler_list.get_handlers(self.context)

        expect(handlers).not_to_be_null()
        expect(handlers).to_length(1)
        url, handler = handlers[0]
        expect(url).to_equal(r"/healthcheck/?")
        expect(handler).to_equal(HealthcheckHandler)

    def test_can_get_handlers_with_custom_url(self):
        ctx = self.get_context()
        ctx.config.HEALTHCHECK_ROUTE = "/health"

        handlers = handler_list.get_handlers(ctx)

        expect(handlers).not_to_be_null()
        expect(handlers).to_length(1)
        url, handler = handlers[0]
        expect(url).to_equal("/health")
        expect(handler).to_equal(HealthcheckHandler)
