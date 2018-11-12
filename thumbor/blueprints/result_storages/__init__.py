#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com


import tornado.gen

from thumbor.lifecycle import Events


class ResultStorage:
    def __init__(self):
        Events.subscribe(
            Events.Imaging.after_parsing_arguments, self.after_parsing_arguments
        )
        Events.subscribe(Events.Imaging.after_finish_request, self.after_finish_request)

    @classmethod
    @tornado.gen.coroutine
    def after_parsing_arguments(cls, sender, request, details):
        response = yield cls.load_transformed_image(
            request, details, details.request_parameters.url
        )

        return response

    @classmethod
    @tornado.gen.coroutine
    def load_transformed_image(cls, request, details, url):
        raise NotImplementedError()

    @classmethod
    @tornado.gen.coroutine
    def after_finish_request(cls, sender, request, details):
        if details.status_code != 200 or details.transformed_image is None:
            return None

        should_store = (
            details.config.RESULT_STORAGE_STORES_UNSAFE
            or not details.request_parameters.unsafe
        )

        if not should_store:
            return None

        response = yield cls.save_source_image(
            request, details, details.request_parameters.url, details.transformed_image
        )

        return response

    @classmethod
    @tornado.gen.coroutine
    def save_transformed_image(cls, request, details, url, transformed_image):
        raise NotImplementedError()
