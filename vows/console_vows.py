#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

import thumbor.console
from thumbor.context import ServerParameters


@Vows.batch
class ConsoleVows(Vows.Context):

    class CanParseArguments(Vows.Context):
        def topic(self):
            server_parameters = thumbor.console.get_server_parameters(['-p', '2000'])
            return server_parameters

        def should_not_be_null(self, topic):
            expect(topic).not_to_be_null()

        def should_be_console(self, topic):
            expect(topic).to_be_instance_of(ServerParameters)

        def should_have_specific_port(self, topic):
            expect(topic.port).to_equal(2000)

        def should_use_the_default_thumbor_app(self, topic):
            expect(topic.app_class).to_equal('thumbor.app.ThumborServiceApp')

    class CanUseACustomApp(Vows.Context):
        def topic(self):
            server_parameters = thumbor.console.get_server_parameters(['-a', 'vows.fixtures.custom_app.MyCustomApp'])
            return server_parameters

        def should_have_my_custom_app_value(self, topic):
            expect(topic.app_class).to_equal('vows.fixtures.custom_app.MyCustomApp')
