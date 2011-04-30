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

from thumbor.loaders.http_loader import load, verify_size

fixture_for = lambda filename: abspath(join(dirname(__file__), 'fixtures', filename))

@Vows.assertion
def to_match_contents_of(topic, filepath):
    assert file(filepath).read() == topic, "Expected body of %s to match topic, but it didn't" % filepath

class HttpLoader(Vows.Context):
    class LoadAndVerifyImage(Vows.Context):
        def topic(self):
            return 'http://s.glbimg.com/jo/g1/f/original/2011/04/29/conselheira_tutelar.jpg'

        class Verify(Vows.Context):
            class WhenInMaxSize(Vows.Context):
                def topic(self, url):
                    return verify_size(url, 50 * 1024)

                def should_return_true_to_fifty_megs(self, topic):
                    expect(topic).to_be_true()

            class WhenOutOfMaxSize(Vows.Context):
                def topic(self, url):
                    return verify_size(url, 1)

                def should_return_false_to_one_kb(self, topic):
                    expect(topic).to_be_false()

        #class Load(Vows.Context):
            #def topic(self, url):
                #return Vows.AsyncTopic(load, url)

            #def should_equal_regular_http_get(self, topic):
                #expect(topic).to_match_contents_of(fixture_for('conselheira_tutelar.jpg'))
