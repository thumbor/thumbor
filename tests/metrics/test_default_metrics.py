# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from unittest import mock

import thumbor.metrics
from tests.base import TestCase
from thumbor.importer import Importer


class DefaultMetricsTestCase(TestCase):
    def get_importer(self):
        importer = Importer(self.config)
        importer.import_modules()
        return importer

    def test_can_create_context_with_default_metrics(self):
        assert self.context is not None
        assert isinstance(
            self.context.metrics, thumbor.metrics.logger_metrics.Metrics
        )

    @mock.patch("thumbor.metrics.BaseMetrics.initialize")
    def test_can_initizalize_when_request_comes(self, mocked_initialize):
        assert mocked_initialize.call_count == 0
        self.fetch("/unsafe/smart/image.jpg")
        assert mocked_initialize.call_count == 1
