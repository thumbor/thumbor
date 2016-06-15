#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from preggy import expect

import thumbor.metrics

from tests.base import TestCase


class DefaultMetricsTestCase(TestCase):
    def test_can_create_context_with_default_metrics(self):
        expect(self.context).not_to_be_null()
        expect(self.context.metrics).to_be_instance_of(thumbor.metrics.logger_metrics.Metrics)
