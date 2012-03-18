#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from thumbor.filters import create_instances
from thumbor.filters.quality import Filter

@Vows.batch
class QualityFilterVows(Vows.Context):
    def topic(self):
        class Any: pass
        ctx = Any()
        ctx.modules = Any()
        ctx.modules.engine = Any()
        ctx.request = Any()
        ctx.request.quality = 0

        filter_instances = create_instances(ctx, [Filter], "quality(10)")

        filter_instances[0].run()
        return ctx.request.quality

    def should_equal_10(self, quality):
        expect(quality).to_equal(10)
