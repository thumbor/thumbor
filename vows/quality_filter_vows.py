#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from thumbor.filters import create_instances, compile_filters
from thumbor.filters.quality import Filter
from thumbor.context import Context, RequestParameters
from thumbor.config import Config

@Vows.batch
class QualityFilterVows(Vows.Context):
    def topic(self):
        conf = Config()
        req = RequestParameters(quality=100)
        ctx = Context(None, conf, None)
        ctx.request = req

        filters = [Filter]
        compile_filters(filters)
        filter_instances = create_instances(ctx, filters, "quality(10)")

        filter_instances[0].run_filter()
        return ctx.request.quality

    def should_equal_10(self, topic):
        expect(topic).to_equal(10)
