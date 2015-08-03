#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import os
import datetime
import librato
from thumbor.metrics import BaseMetrics


class Metrics(BaseMetrics):

    @classmethod
    def queue(cls, config):
        """
        Cached Librato queue for batch submitting
        """
        if not hasattr(cls, "_queue"):
            api = librato.connect(config.LIBRATO_USER, config.LIBRATO_TOKEN)
            cls._queue = api.new_queue(auto_submit_count=config.LIBRATO_QUEUE_LENGTH)

        return cls._queue

    def incr(self, metricname, value=1):
        Metrics.queue(self.config).add(self._prefixed_name(metricname), value)

    def timing(self, metricname, value):
        Metrics.queue(self.config).add(self._prefixed_name(metricname), value)

    def _prefixed_name(self, metricname):
        return "%s.%s" % (self.config.LIBRATO_NAME_PREFIX, metricname)
