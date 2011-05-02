#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from thumbor.url import Url

def ctx(**kw):
    class Context(Vows.Context):
        def topic(self):
            return Url.generate_options(**kw)

    return Context

@Vows.batch
class UrlVows(Vows.Context):

    class Minimum(ctx(width=300, height=200)):

        def should_return_proper_url(self, topic):
            expect(topic).to_equal('300x200')

    class Smart(ctx(width=300, height=200, smart=True)):

        def should_return_proper_url(self, topic):
            expect(topic).to_equal('300x200/smart')

    class Alignments(ctx(halign='left', valign='top')):

        def should_return_proper_url(self, topic):
            expect(topic).to_equal('left/top')


