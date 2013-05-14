#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from thumbor.context import Context, ServerParameters


@Vows.batch
class ContextVows(Vows.Context):

    class CanCreateContext(Vows.Context):
        def topic(self):
            ctx = Context()
            return ctx

        def should_not_be_null(self, topic):
            expect(topic).not_to_be_null()

        def should_be_context(self, topic):
            expect(topic).to_be_instance_of(Context)


@Vows.batch
class ServerParameterVows(Vows.Context):

    class CanCreateServerParameters(Vows.Context):
        def topic(self):
            params = ServerParameters(port=8888,
                                      ip='127.0.0.1',
                                      config_path='config_path',
                                      keyfile=None,
                                      log_level='log_level',
                                      app_class=None)
            return params

        def should_not_be_null(self, topic):
            expect(topic).not_to_be_null()

        def should_be_context(self, topic):
            expect(topic).to_be_instance_of(ServerParameters)

        def should_have_proper_port(self, topic):
            expect(topic.port).to_equal(8888)

        def should_have_proper_ip(self, topic):
            expect(topic.ip).to_equal('127.0.0.1')

        def should_have_proper_config_path(self, topic):
            expect(topic.config_path).to_equal('config_path')

        def should_have_null_keyfile(self, topic):
            expect(topic.keyfile).to_be_null()

        def should_have_proper_log_level(self, topic):
            expect(topic.log_level).to_equal('log_level')

        def should_have_null_app_class(self, topic):
            expect(topic.app_class).to_be_null()
