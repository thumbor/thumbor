#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from thumbor.handlers import BaseHandler
from thumbor.context import Context
from thumbor.config import Config
from thumbor.app import ThumborServiceApp
from mock import MagicMock


@Vows.batch
class BaseHandlerVows(Vows.Context):

    class ShouldStoreHeaderOnContext(Vows.Context):
        def topic(self):
            ctx = Context(None, Config(), None)
            application = ThumborServiceApp(ctx)
            handler = BaseHandler(application, MagicMock())
            handler._transforms = []
            return handler

        def should_be_ThumborServiceApp(self, topic):
            mocked_context = MagicMock(**{'config.MAX_AGE_TEMP_IMAGE': 30})
            topic._write_results_to_client(mocked_context, '', 'image/jpeg')
            expect(mocked_context.headers).to_include('Expires')
            expect(mocked_context.headers).to_include('Server')
            expect(mocked_context.headers).to_include('Cache-Control')
            expect(mocked_context.headers['Content-Type']).to_equal('image/jpeg')
