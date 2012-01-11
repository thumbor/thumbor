#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

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
