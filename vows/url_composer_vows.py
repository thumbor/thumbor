#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from thumbor.url_composer import main

@Vows.batch
class AppVows(Vows.Context):

    class ErrorsWhenNoArguments(Vows.Context):
        def topic(self):
            return main([])

        def should_be_null(self, topic):
            expect(topic).to_be_null()


    #class WhenImagePassed(Vows.Context):
        #def topic(self):
            #return main([

            #])
