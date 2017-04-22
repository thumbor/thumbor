#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect

from thumbor.context import Context
from thumbor.importer import Importer
from thumbor.config import Config
import thumbor.metrics

from tests.base import TestCase


class PrometheusMetricsTestCase(TestCase):
    def get_context(self):
        conf = Config()
        conf.METRICS = 'thumbor.metrics.prometheus_metrics'
        imp = Importer(conf)
        imp.import_modules()
        return Context(None, conf, imp)

    def test_should_initialize_metrics(self):
        expect(self.context.metrics).to_be_instance_of(thumbor.metrics.prometheus_metrics.Metrics)

    def test_should_not_fail_on_use(self):
        expect(self.context.metrics.incr('test.count')).not_to_be_an_error()
        expect(self.context.metrics.incr('test.count', 2)).not_to_be_an_error()
        expect(self.context.metrics.timing('test.time', 100)).not_to_be_an_error()

    def test_should_present_metrics(self):
        self.context.metrics.incr('test.counter')
        self.context.metrics.incr('test.counter', 5)
        self.context.metrics.timing('test.timer', 150)
        self.context.metrics.timing('test.timer', 350)

        self.http_client.fetch('http://localhost:8000', self.stop)
        response = self.wait()
        expect(response.body).to_include('thumbor_test_counter 6')
        expect(response.body).to_include('thumbor_test_timer_count 2')
        expect(response.body).to_include('thumbor_test_timer_sum 500')
