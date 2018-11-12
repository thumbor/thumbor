#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import tornado.gen

from thumbor.lifecycle import Events


class Loader:
    def __init__(self):
        Events.subscribe(Events.Imaging.load_source_image, self.on_load_source_image)

    @classmethod
    @tornado.gen.coroutine
    def on_load_source_image(cls, sender, request, details):
        res = yield cls.load_source_image(request, details)

        return res

    @classmethod
    @tornado.gen.coroutine
    def load_source_image(cls, request, details):
        raise NotImplementedError()
