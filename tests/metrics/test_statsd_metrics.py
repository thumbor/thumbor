#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect

import thumbor.metrics
from tests.base import TestCase
from thumbor.config import Config
from thumbor.context import Context
from thumbor.importer import Importer


class StatsdMetricsTestCase(TestCase):
    def get_context(self):
        conf = Config()
        conf.METRICS = "thumbor.metrics.statsd_metrics"
        imp = Importer(conf)
        imp.import_modules()
        return Context(None, conf, imp)

    def test_should_initialize_metrics(self):
        expect(self.context.metrics).to_be_instance_of(
            thumbor.metrics.statsd_metrics.Metrics
        )

    def test_should_not_fail_on_use(self):
        expect(self.context.metrics.incr("test.count")).not_to_be_an_error()
        expect(self.context.metrics.incr("test.count", 2)).not_to_be_an_error()
        expect(
            self.context.metrics.timing("test.time", 100)
        ).not_to_be_an_error()
