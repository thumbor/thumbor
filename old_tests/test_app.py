#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from unittest import TestCase
import mock

from preggy import expect

from thumbor.app import (
    ThumborServiceApp
)
from thumbor.url import Url


class AppTestCase(TestCase):
    def test_can_create_app(self):
        ctx = mock.Mock()
        app = ThumborServiceApp(ctx)
        expect(app).not_to_be_null()
        expect(app.context).to_equal(ctx)

    def test_can_get_handlers(self):
        ctx = mock.Mock(
            config=mock.Mock(
                UPLOAD_ENABLED=False,
                USE_BLACKLIST=False,
            )
        )
        app = ThumborServiceApp(ctx)

        handlers = app.get_handlers()
        expect(handlers).to_length(2)
        expect(handlers[0][0]).to_equal(r'/healthcheck')
        expect(handlers[1][0]).to_equal(Url.regex())

    def test_can_get_handlers_with_upload(self):
        ctx = mock.Mock(
            config=mock.Mock(
                UPLOAD_ENABLED=True,
                USE_BLACKLIST=False,
            )
        )
        app = ThumborServiceApp(ctx)

        handlers = app.get_handlers()
        expect(handlers).to_length(4)

    def test_can_get_handlers_with_blacklist(self):
        ctx = mock.Mock(
            config=mock.Mock(
                UPLOAD_ENABLED=False,
                USE_BLACKLIST=True,
            )
        )
        app = ThumborServiceApp(ctx)

        handlers = app.get_handlers()
        expect(handlers).to_length(3)
