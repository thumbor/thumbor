#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import logging

from pyvows import Vows, expect

from thumbor.utils import logger, real_import


@Vows.batch
class UtilVows(Vows.Context):

    class Logger(Vows.Context):
        def topic(self):
            return logger

        def should_be_instance_of_python_logger(self, topic):
            expect(topic).to_be_instance_of(logging.Logger)

        def should_not_be_null(self, topic):
            expect(topic).not_to_be_null()

        def should_not_be_an_error(self, topic):
            expect(topic).not_to_be_an_error()

    class RealImport(Vows.Context):

        class WhenRegularModules(Vows.Context):
            def topic(self):
                return real_import('pyvows')

            def should_have_expect(self, topic):
                expect(topic.expect).not_to_be_null()

        class WhenUsingSubmodules(Vows.Context):
            def topic(self):
                return real_import('thumbor.utils')

            def should_not_be_an_error(self, topic):
                expect(topic).not_to_be_an_error()

            def should_not_be_null(self, topic):
                expect(topic).not_to_be_null()

            def should_return_module(self, topic):
                expect(topic.logger).not_to_be_null()
