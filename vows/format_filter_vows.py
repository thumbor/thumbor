#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from thumbor.context import Context, RequestParameters
from thumbor.config import Config
from thumbor.importer import Importer
from thumbor.filters.format import Filter


@Vows.batch
class FormatFilterVows(Vows.Context):
    class DisallowsInvalidContext(Vows.Context):
        def topic(self):
            conf = Config()
            imp = Importer(conf)
            imp.filters = [Filter]
            ctx = Context(None, conf, imp)
            ctx.request = RequestParameters()

            filter_instances = ctx.filters_factory.create_instances(ctx, "format(invalid)")

            filter_instances[0].run()

        def should_be_none(self, format):
            expect(format).to_be_null()

    class SetsProperFormat(Vows.Context):
        def topic(self):
            conf = Config()
            imp = Importer(conf)
            imp.filters = [Filter]
            ctx = Context(None, conf, imp)
            ctx.request = RequestParameters()

            filter_instances = ctx.filters_factory.create_instances(ctx, "format(webp)")

            filter_instances[0].run()
            return ctx.request.format

        def should_equal_10(self, format):
            expect(format).to_equal("webp")
