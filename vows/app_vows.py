#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from thumbor.app import ThumborServiceApp

@Vows.batch
class AppVows(Vows.Context):

    class CanCreateApp(Vows.Context):
        def topic(self):
            return ThumborServiceApp()

        def should_be_ThumborServiceApp(self, topic):
            expect(topic).to_be_instance_of(ThumborServiceApp)

