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
        ctx = { 'quality': 100, 'engine': None }
        filter_instances = create_instances(ctx, [Filter], "quality(10)")
        filter_instances[0].run_filter()
        return ctx['quality']

    def should_equal_10(self, topic):
        expect(topic).to_equal(10)
