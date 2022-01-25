#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from unittest import mock

from preggy import expect

import thumbor.metrics
from tests.base import TestCase
from thumbor.importer import Importer


class DefaultMetricsTestCase(TestCase):
    def get_importer(self):
        importer = Importer(self.config)
        importer.import_modules()
        return importer

    def test_can_create_context_with_default_metrics(self):
        expect(self.context).not_to_be_null()
        expect(self.context.metrics).to_be_instance_of(
            thumbor.metrics.logger_metrics.Metrics
        )

    @mock.patch("thumbor.metrics.BaseMetrics.initialize")
    def test_can_initizalize_when_request_comes(self, mocked_initialize):
        expect(mocked_initialize.call_count).to_equal(0)
        self.fetch("/unsafe/smart/image.jpg")
        expect(mocked_initialize.call_count).to_equal(1)
