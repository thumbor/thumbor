#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import abspath, join, dirname

from tornado.options import options, parse_config_file
from pyvows import Vows, expect

from thumbor.loaders.http_loader import load

config_file_path = lambda filename: abspath(join(dirname(__file__), 'fixtures', filename))

@Vows.batch
class HttpLoader(Vows.Context):
    class Options(Vows.Context):

        class FirstDefaults(Vows.Context):
            class AllowedSources(Vows.Context):
                def topic(self):
                    return options.ALLOWED_SOURCES

                def should_be_empty(self, topic):
                    expect(topic).to_be_empty()

            class MaxSourceSize(Vows.Context):
                def topic(self):
                    return options.MAX_SOURCE_SIZE

                def should_be_numeric(self, topic):
                    expect(topic).to_be_numeric()

                def should_be_zero(self, topic):
                    expect(topic).to_equal(0)

            class RequestTimeoutSeconds(Vows.Context):
                def topic(self):
                    return options.REQUEST_TIMEOUT_SECONDS

                def should_be_numeric(self, topic):
                    expect(topic).to_be_numeric()

                def should_be_two_minutes(self, topic):
                    expect(topic).to_equal(120)

            class ThenSpecified(Vows.Context):
                def topic(self):
                    parse_config_file(config_file_path('http_loader_options.py'))

                class AllowedSources(Vows.Context):
                    def topic(self):
                        return options.ALLOWED_SOURCES

                    def should_be_equal_to_something(self, topic):
                        expect(topic).to_be_like(['s.glbimg.com'])

                class MaxSourceSize(Vows.Context):
                    def topic(self):
                        return options.MAX_SOURCE_SIZE

                    def should_be_numeric(self, topic):
                        expect(topic).to_be_numeric()

                    def should_be_zero(self, topic):
                        expect(topic).to_equal(5000)

                class RequestTimeoutSeconds(Vows.Context):
                    def topic(self):
                        return options.REQUEST_TIMEOUT_SECONDS

                    def should_be_numeric(self, topic):
                        expect(topic).to_be_numeric()

                    def should_be_three_minutes(self, topic):
                        expect(topic).to_equal(180)

    #class WhenInstanceCreated(Vows.Context):
        #def topic(self):
            #return HttpLoader()
