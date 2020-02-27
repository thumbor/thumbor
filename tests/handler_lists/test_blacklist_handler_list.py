#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect

import thumbor.handler_lists.blacklist as handler_list
from thumbor.handlers.blacklist import BlacklistHandler
from thumbor.testing import TestCase


class BlacklistHandlerListTestCase(TestCase):
    def test_can_get_handlers(self):
        ctx = self.get_context()
        ctx.config.USE_BLACKLIST = True

        handlers = handler_list.get_handlers(ctx)

        expect(handlers).not_to_be_null()
        expect(handlers).to_length(1)
        url, handler, initializer = handlers[0]
        expect(url).to_equal(r"/blacklist/?")
        expect(handler).to_equal(BlacklistHandler)
        expect(initializer).to_equal({"context": ctx})

    def test_can_disable_blacklist(self):
        ctx = self.get_context()
        ctx.config.UPLOAD_ENABLED = False

        handlers = handler_list.get_handlers(ctx)

        expect(handlers).not_to_be_null()
        expect(handlers).to_be_empty()
