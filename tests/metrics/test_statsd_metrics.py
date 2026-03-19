# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

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
        assert isinstance(
            self.context.metrics, thumbor.metrics.statsd_metrics.Metrics
        )

    def test_should_not_fail_on_use(self):
        self.context.metrics.incr("test.count")
        self.context.metrics.incr("test.count", 2)
        self.context.metrics.timing("test.time", 100)
