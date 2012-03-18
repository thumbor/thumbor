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
from thumbor.filters.quality import Filter

@Vows.batch
class QualityFilterVows(Vows.Context):
    def topic(self):
        conf = Config()
        imp = Importer(conf)
        imp.filters = [Filter]
        ctx = Context(None, conf, imp)
        ctx.request = RequestParameters()

        filter_instances = ctx.filters_factory.create_instances(ctx, "quality(10)")

        filter_instances[0].run()
        return ctx.request.quality

    def should_equal_10(self, quality):
        expect(quality).to_equal(10)
