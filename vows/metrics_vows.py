#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from thumbor.context import Context, ServerParameters
from thumbor.importer import Importer
from thumbor.config import Config
import thumbor.metrics

@Vows.batch
class MetricsVows(Vows.Context):

    class CanCreateContextWithDefaultMetrics(Vows.Context):

        def topic(self):
            ctx = Context()
            return ctx

        def should_not_be_null(self, topic):
            expect(topic).not_to_be_null()

        def should_be_context(self, topic):
            expect(topic.metrics).to_be_instance_of(
                thumbor.metrics.logger_metrics.Metrics)

    class CanCreateContextWithLoggerMetrics(Vows.Context):

        def topic(self):
            conf = Config()
            conf.METRICS = 'thumbor.metrics.logger_metrics'
            imp = Importer(conf)
            imp.import_modules()
            return Context(None, conf, imp)

        def should_initialize_metrics(self, topic):
            expect(topic.metrics).to_be_instance_of(
                thumbor.metrics.logger_metrics.Metrics)

        def should_not_fail_on_use(self, topic):
            expect(topic.metrics.incr('test.count')).not_to_be_an_error()
            expect(topic.metrics.incr('test.count', 2)).not_to_be_an_error()
            expect(topic.metrics.timing('test.time', 100)).not_to_be_an_error()

    class CanCreateContextWithStatsdMetrics(Vows.Context):

        def topic(self):
            conf = Config()
            conf.METRICS = 'thumbor.metrics.statsd_metrics'
            imp = Importer(conf)
            imp.import_modules()
            return Context(None, conf, imp)

        def should_initialize_metrics(self, topic):
            expect(topic.metrics).to_be_instance_of(
                thumbor.metrics.statsd_metrics.Metrics)

        def should_not_fail_on_use(self, topic):
            expect(topic.metrics.incr('test.count')).not_to_be_an_error()
            expect(topic.metrics.incr('test.count', 2)).not_to_be_an_error()
            expect(topic.metrics.timing('test.time', 100)).not_to_be_an_error()
