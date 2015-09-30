#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from thumbor.context import Context, RequestParameters
from thumbor.config import Config
from thumbor.importer import Importer
from thumbor.filters.rotate import Filter
import thumbor.filters


class RotateEngine:
    def __init__(self):
        self.rotate_val = None

    def rotate(self, rotate_val):
        self.rotate_val = rotate_val

    def is_multiple(self):
        return False


@Vows.batch
class RotateFilterVows(Vows.Context):
    class DisallowsInvalidContext(Vows.Context):
        def topic(self):
            conf = Config()
            imp = Importer(conf)
            imp.filters = [Filter]
            ctx = Context(None, conf, imp)
            ctx.request = RequestParameters()

            runner = ctx.filters_factory.create_instances(ctx, "rotate(91)")
            filter_instances = runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]

            filter_instances[0].engine = RotateEngine()
            filter_instances[0].run()

            return filter_instances[0].engine.rotate_val

        def should_be_none(self, rotate):
            expect(rotate).to_be_null()

    class RotateProperly(Vows.Context):
        def topic(self):
            conf = Config()
            imp = Importer(conf)
            imp.filters = [Filter]
            ctx = Context(None, conf, imp)
            ctx.request = RequestParameters()

            runner = ctx.filters_factory.create_instances(ctx, "rotate(90)")
            filter_instances = runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]

            filter_instances[0].engine = RotateEngine()
            filter_instances[0].run()

            return filter_instances[0].engine.rotate_val

        def should_equal_90(self, rotate):
            expect(rotate).to_equal(90)

    class NormalizeRotate(Vows.Context):
        def topic(self):
            conf = Config()
            imp = Importer(conf)
            imp.filters = [Filter]
            ctx = Context(None, conf, imp)
            ctx.request = RequestParameters()

            runner = ctx.filters_factory.create_instances(ctx, "rotate(540)")
            filter_instances = runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]

            filter_instances[0].engine = RotateEngine()
            filter_instances[0].run()

            return filter_instances[0].engine.rotate_val

        def should_equal_90(self, rotate):
            expect(rotate).to_equal(180)
