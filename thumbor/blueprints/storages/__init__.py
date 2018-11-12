#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import tornado.gen

from thumbor.lifecycle import Events


class Storage:
    def __init__(self):
        Events.subscribe(
            Events.Imaging.before_loading_source_image, self.before_loading_source_image
        )
        Events.subscribe(
            Events.Imaging.after_loading_source_image, self.after_loading_source_image
        )

    @classmethod
    @tornado.gen.coroutine
    def before_loading_source_image(cls, sender, request, details):
        response = yield cls.load_source_image(
            request, details, details.request_parameters.image_url
        )

        return response

    @classmethod
    @tornado.gen.coroutine
    def load_source_image(cls, request, details, image_url):
        raise NotImplementedError()

    @classmethod
    @tornado.gen.coroutine
    def after_loading_source_image(cls, sender, request, details):
        response = yield cls.save_source_image(
            request, details, details.request_parameters.image_url, details.source_image
        )

        return response

    @classmethod
    @tornado.gen.coroutine
    def save_source_image(cls, request, details, image_url, source_image):
        raise NotImplementedError()
