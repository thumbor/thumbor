#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

'''
Handler responsible for:
    * Thumbor's image requests;
    * Thumbor's metadata requests.
'''

import tornado.web
import tornado.gen

import thumbor.context
from thumbor.lifecycle import Events
from thumbor.blueprints.loaders.http import plug_into_lifecycle as http_loader_init


# TODO: proper loading of blueprints
http_loader_init()


class RequestDetails(object):
    def __init__(self):
        self.finish_early = False
        self.status_code = 200
        self.body = None
        self.headers = {}
        self.source_image = None


class CoreHandler(tornado.web.RequestHandler):

    @tornado.gen.coroutine
    def finish_request(self, details):
        yield Events.trigger(Events.Imaging.before_finish_request, self, request=self.request, details=details)
        self.set_status(details.status_code)
        self.write(details.body)
        for header, value in details.headers:
            self.set-header(header, value)
        yield Events.trigger(Events.Imaging.after_finish_request, self, request=self.request, details=details)

    @tornado.gen.coroutine
    def get(self, **kw):
        details = RequestDetails()

        finish = yield self._before_request(details=details, kw=kw)
        if finish:
            return

        req, finish = yield self._parse_arguments(details, kw)
        if finish:
            return

        yield self._load_image(details, req)
        if details.finish_early:
            yield self.finish_request(details)
            return

        # TODO: this is temp
        details.body = details.source_image

        yield self.finish_request(details)
        req = None
        details = None

    @tornado.gen.coroutine
    def _before_request(self, details, kw):
        yield Events.trigger(Events.Imaging.request_received, self, request=self.request, details=details, kw=kw)
        if details.finish_early:
            yield self.finish_request(details)
            return True
        return False

    @tornado.gen.coroutine
    def _parse_arguments(self, details, kw):
        yield Events.trigger(Events.Imaging.before_parsing_arguments, self, request=self.request, details=details, arguments=kw)
        if details.finish_early:
            yield self.finish_request(details)
            return None, True

        req = thumbor.context.RequestParameters.from_route_arguments(self.request, kw)
        yield Events.trigger(Events.Imaging.after_parsing_arguments, self, request=self.request, details=details, arguments=kw)
        if details.finish_early:
            yield self.finish_request(details)
            return None, True

        return req, False

    @tornado.gen.coroutine
    def _load_image(self, details, req):
        yield Events.trigger(
            Events.Imaging.before_loading_source_image, self,
            request=self.request, details=details, request_parameters=req,
        )
        if details.finish_early:
            yield self.finish_request(details)
            return None, True

        yield Events.trigger(
            Events.Imaging.load_source_image, self,
            request=self.request, details=details, request_parameters=req
        )

        if details.source_image is None:
            yield Events.trigger(
                Events.Imaging.source_image_not_found, self,
                request=self.request, details=details, request_parameters=req
            )
            if details.status_code == 200:
                details.status_code = 404
                details.body = "Source Image was not found at %s" % req.image_url
            yield self.finish_request(details)
            return None, True

        yield Events.trigger(
            Events.Imaging.after_loading_source_image, self,
            request=self.request, details=details, request_parameters=req,
        )
        if details.finish_early:
            yield self.finish_request(details)
            return None, True

        return req, False
