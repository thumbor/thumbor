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

    class WhenProperArguments(Vows.Context):
        def topic(self):
            return main([
                "-k", "MY-SECURITY-KEY",
                "-w", "200",
                "-e", "300",
                "myserver.com/myimg.jpg"
            ])

        def should_be_proper_url(self, topic):
            expect(topic).to_equal('/G_dykuWBGyEil5JnNh9cBke0Ajo=/200x300/myserver.com/myimg.jpg')

    class WhenOldFormat(Vows.Context):
        def topic(self):
            return main([
                "-k", "MY-SECURITY-KEY",
                "-w", "200",
                "-e", "300",
                "--old-format",
                "myserver.com/myimg.jpg"
            ])

        def should_be_proper_url(self, topic):
            expect(topic).to_equal('/6LSog0KmY0NQg8GK4Tsti0FAR9emvaF4xfyLY3FUmOI0HVcqF8HxibsAjVCbxFfl/myserver.com/myimg.jpg')
