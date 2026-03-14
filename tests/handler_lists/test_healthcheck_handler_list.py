# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import thumbor.handler_lists.healthcheck as handler_list
from thumbor.handlers.healthcheck import HealthcheckHandler
from thumbor.testing import TestCase


class HealthcheckHandlerListTestCase(TestCase):
    def test_can_get_handlers(self):
        handlers = handler_list.get_handlers(self.context)

        assert handlers is not None
        assert len(handlers) == 1
        url, handler = handlers[0]
        assert url == r"/healthcheck/?"
        assert handler == HealthcheckHandler

    def test_can_get_handlers_with_custom_url(self):
        ctx = self.get_context()
        ctx.config.HEALTHCHECK_ROUTE = "/health"

        handlers = handler_list.get_handlers(ctx)

        assert handlers is not None
        assert len(handlers) == 1
        url, handler = handlers[0]
        assert url == "/health"
        assert handler == HealthcheckHandler
