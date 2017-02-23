#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from prometheus_client import Counter, start_http_server, Summary
from thumbor.metrics import BaseMetrics


class Metrics(BaseMetrics):

    def __init__(self, config):
        super(Metrics, self).__init__(config)

        if not hasattr(Metrics, 'http_server_started'):
            start_http_server(config.PROMETHEUS_SCRAPE_PORT)
            Metrics.http_server_started = True
            Metrics.counters = {}
            Metrics.summaries = {}

        # hard coded mapping right now
        self.mapping = {
                'response.status': ['statuscode'],
                'response.format': ['extension'],
                'response.bytes': ['extension'],
                'original_image.status': ['statuscode'],
                'original_image.fetch': ['statuscode', 'networklocation'],
                'response.time': ['statuscode_extension'],
        }

    def incr(self, metricname, value=1):
        name, labels = self.__data(metricname)

        if name not in Metrics.counters:
            Metrics.counters[name] = Counter(name, name, labels.keys())

        counter = Metrics.counters[name]

        if len(labels) != 0:
            counter = counter.labels(**labels)

        counter.inc(value)

    def timing(self, metricname, value):
        name, labels = self.__data(metricname)

        if name not in Metrics.summaries:
            Metrics.summaries[name] = Summary(name, name, labels.keys())

        summary = Metrics.summaries[name]

        if len(labels) != 0:
            summary = summary.labels(**labels)

        summary.observe(value)

    def __data(self, metricname):
        basename = self.__basename(metricname)

        return (self.__format(basename), self.__labels(basename, metricname))

    def __format(self, basename):
        # stolen from https://github.com/prometheus/statsd_exporter
        # _ -> __
        # - -> __
        # . -> _
        return basename.replace('_', '__').replace('-', '__').replace('.', '_')

    def __labels(self, name, metricname):
        if name not in self.mapping:
            return {}

        # the split('.', MAXSPLIT) is mainly necessary to get the correct
        # stuff for original_image.fetch where the networklocation is
        # something like 'domain' so like 'test.com' and would be splitted at
        # least 1 time too often
        values = metricname.replace(name + '.', '').split('.', len(self.mapping[name])-1)
        labels = {}
        for index, label in enumerate(self.mapping[name]):
            labels[label] = values[index]

        return labels

    def __basename(self, metricname):
        for mapped in self.mapping.keys():
            if metricname.startswith(mapped + "."):
                metricname = mapped
        return "thumbor.{0}".format(metricname)
