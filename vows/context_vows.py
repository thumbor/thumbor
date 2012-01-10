#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from thumbor.context import Context

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
 
