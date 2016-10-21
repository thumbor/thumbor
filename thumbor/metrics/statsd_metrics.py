#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import statsd
from thumbor.metrics import BaseMetrics


class Metrics(BaseMetrics):

    @classmethod
    def client(cls, config):
        """
        Cache statsd client so it doesn't do a DNS lookup
        over and over
        """
        if not hasattr(cls, "_client"):
            cls._client = statsd.StatsClient(config.STATSD_HOST, config.STATSD_PORT, config.STATSD_PREFIX)
        return cls._client

    def incr(self, metricname, value=1):
        Metrics.client(self.config).incr(metricname, value)

    def timing(self, metricname, value):
        Metrics.client(self.config).timing(metricname, value)
