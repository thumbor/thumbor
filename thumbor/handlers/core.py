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
import magic

import thumbor.context
from thumbor.lifecycle import Events

# Blueprints
from thumbor.blueprints.loaders.http import plug_into_lifecycle as http_loader_init
from thumbor.blueprints.storages.file import plug_into_lifecycle as file_storage_init
from thumbor.blueprints.engines.pillow import plug_into_lifecycle as pillow_engine_init


# TODO: proper loading of blueprints
http_loader_init()
file_storage_init()
pillow_engine_init()


class ConfigWrapper(object):
    def __init__(self, config):
        self._config = config

    def __getattr__(self, name):
        if name != '_config' and name not in self.__dict__:
            return getattr(self._config, name)
        return object.__getattr__(name)


class RequestDetails(object):
    def __init__(self, config, request_parameters=None):
        self.mimetype = None
        self.finish_early = False
        self.status_code = 200
        self.body = None
        self.headers = {}
        self.source_image = None
        self.transformed_image = None
        self.request_parameters = request_parameters
        self._config = config
        self.config = ConfigWrapper(config)
        self.metadata = {}


class CoreHandler(tornado.web.RequestHandler):

    @tornado.gen.coroutine
    def finish_request(self, details):
        yield Events.trigger(Events.Imaging.before_finish_request, self, request=self.request, details=details)
        self.set_status(details.status_code)
        self.write(details.body)

        if details.body is not None:
            if 'Content-Type' not in details.headers:
                details.headers['Content-Type'] = details.mimetype

            details.headers['Content-Length'] = len(details.body)

        for header, value in details.headers.items():
            self.set_header(header, value)

        yield Events.trigger(Events.Imaging.after_finish_request, self, request=self.request, details=details)

    @tornado.gen.coroutine
    def get(self, **kw):
        details = RequestDetails(self.application.context.config)

        finish = yield self._before_request(details=details, kw=kw)
        if finish:
            return

        req, finish = yield self._parse_arguments(details, kw)
        if finish:
            return

        if details.transformed_image is not None:
            details.body = details.transformed_image
            self.determine_mimetype(details, details.body)
            yield self.finish_request(details)
            return

        finish = yield self._load_image(details)
        if finish:
            return

        self.determine_mimetype(details, details.source_image)

        finish = yield self._transform_image(details)
        if finish:
            return

        details.body = details.transformed_image
        self.determine_mimetype(details, details.body)

        yield self.finish_request(details)
        del(req)
        del(details)
        del(finish)

    def determine_mimetype(self, details, buffer):
        details.mimetype = magic.from_buffer(buffer[:1024], True)

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
        details.request_parameters = req
        yield Events.trigger(
            Events.Imaging.after_parsing_arguments, self,
            request=self.request, details=details,
        )
        if details.finish_early:
            yield self.finish_request(details)
            return None, True

        return req, False

    @tornado.gen.coroutine
    def _load_image(self, details):
        # Before loading source image
        yield Events.trigger(
            Events.Imaging.before_loading_source_image, self,
            request=self.request, details=details,
        )
        if details.finish_early:
            yield self.finish_request(details)
            return True

        if details.source_image is not None:
            # Source Image was found in storage
            yield Events.trigger(
                Events.Imaging.source_image_already_loaded, self,
                request=self.request, details=details,
            )
        else:
            # Source image must be loaded
            yield Events.trigger(
                Events.Imaging.load_source_image, self,
                request=self.request, details=details,
            )

            if details.source_image is None:
                # Source image could not be loaded
                yield Events.trigger(
                    Events.Imaging.source_image_not_found, self,
                    request=self.request, details=details,
                )
                if details.status_code == 200:
                    details.status_code = 404
                    details.body = "Source Image was not found at %s" % details.request_parameters.image_url
                yield self.finish_request(details)
                return True

        # Source image has been loaded successfully
        yield Events.trigger(
            Events.Imaging.after_loading_source_image, self,
            request=self.request, details=details,
        )
        if details.finish_early:
            yield self.finish_request(details)
            return True

        return False

    @tornado.gen.coroutine
    def _transform_image(self, details):
        # Before transforming the image
        yield Events.trigger(
            Events.Imaging.before_transforming_image, self,
            request=self.request, details=details,
        )
        if details.finish_early:
            yield self.finish_request(details)
            return True

        # Image transformation phases
        for i in range(5):
            ev = Events.get('imaging.image_transforming_phase_%d' % (i + 1))
            yield Events.trigger(
                ev, self,
                request=self.request, details=details,
            )
            if details.finish_early:
                yield self.finish_request(details)
                return True

        if details.transformed_image is None:
            details.transformed_image = details.source_image

        # After transforming the image
        yield Events.trigger(
            Events.Imaging.after_transforming_image, self,
            request=self.request, details=details,
        )
        if details.finish_early:
            yield self.finish_request(details)
            return True

        return False
