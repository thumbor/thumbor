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
from thumbor.handlers.request_details import RequestDetails
from thumbor import Engine
from thumbor.utils import logger

TRIM_ENABLED = True
try:
    from thumbor.ext.filters import _bounding_box
except ImportError:
    logger.info("Error importing bounding_box filter, trimming won't work")
    TRIM_ENABLED = False


def determine_mimetype(details, buffer):
    'Determines the mimetype of the specified buffer and sets it in the details.'
    details.mimetype = magic.from_buffer(buffer[:1024], True)


class CoreHandler(tornado.web.RequestHandler):  # pylint: disable=abstract-method
    'Handler responsible for transforming images'

    @tornado.gen.coroutine
    def finish_request(self, details):
        '''
        Finishes the request with the parameters specified in the details instance.
        '''
        yield Events.trigger(
            Events.Imaging.before_finish_request,
            self,
            request=self.request,
            details=details)
        self.set_status(details.status_code)
        self.write(details.body)

        if details.body is not None:
            if 'Content-Type' not in details.headers:
                details.headers['Content-Type'] = details.mimetype

            details.headers['Content-Length'] = len(details.body)

        for header, value in details.headers.items():
            self.set_header(header, value)

        yield Events.trigger(
            Events.Imaging.after_finish_request,
            self,
            request=self.request,
            details=details)

    @tornado.gen.coroutine
    def get(self, *args, **kw):  # pylint: disable=too-many-return-statements
        details = RequestDetails(self.application.context.config)

        finish = yield self._before_request(details=details, kw_args=kw)
        if finish:
            return

        req, finish = yield self._parse_arguments(details, kw)
        if finish:
            return

        if details.transformed_image is not None:
            details.body = details.transformed_image
            determine_mimetype(details, details.body)
            yield self.finish_request(details)
            return

        finish = yield self._load_image(details)
        if finish:
            return

        determine_mimetype(details, details.source_image)

        details.build_filters_map()

        finish = yield self._read_image(details)
        if finish:
            return

        finish = yield self._transform_image(details)
        if finish:
            return

        finish = yield self._serialize_image(details)
        if finish:
            return

        details.body = details.transformed_image
        determine_mimetype(details, details.body)

        yield self.finish_request(details)

        # Cleaning up to explicitly signal the GC
        del req
        del details
        del finish

    @tornado.gen.coroutine
    def _before_request(self, details, kw_args):
        yield Events.trigger(
            Events.Imaging.request_received,
            self,
            request=self.request,
            details=details,
            kw=kw_args)
        if details.finish_early:
            yield self.finish_request(details)
            return True
        return False

    @tornado.gen.coroutine
    def _parse_arguments(self, details, kw_args):
        yield Events.trigger(
            Events.Imaging.before_parsing_arguments,
            self,
            request=self.request,
            details=details,
            arguments=kw_args)
        if details.finish_early:
            yield self.finish_request(details)
            return None, True

        req = thumbor.context.RequestParameters.from_route_arguments(
            self.request, kw_args)
        details.request_parameters = req
        yield Events.trigger(
            Events.Imaging.after_parsing_arguments,
            self,
            request=self.request,
            details=details,
        )
        if details.finish_early:
            yield self.finish_request(details)
            return None, True

        return req, False

    @tornado.gen.coroutine
    def _load_image(self, details):
        # Before loading source image
        yield Events.trigger(
            Events.Imaging.before_loading_source_image,
            self,
            request=self.request,
            details=details,
        )
        if details.finish_early:
            yield self.finish_request(details)
            return True

        if details.source_image is not None:
            # Source Image was found in storage
            yield Events.trigger(
                Events.Imaging.source_image_already_loaded,
                self,
                request=self.request,
                details=details,
            )
        else:
            # Source image must be loaded
            yield Events.trigger(
                Events.Imaging.load_source_image,
                self,
                request=self.request,
                details=details,
            )

            if details.source_image is None:
                # Source image could not be loaded
                yield Events.trigger(
                    Events.Imaging.source_image_not_found,
                    self,
                    request=self.request,
                    details=details,
                )
                if details.status_code == 200:
                    details.status_code = 404
                    msg = "Source Image was not found at %s" % details.request_parameters.image_url
                    details.body = msg
                yield self.finish_request(details)
                return True

        # Source image has been loaded successfully
        yield Events.trigger(
            Events.Imaging.after_loading_source_image,
            self,
            request=self.request,
            details=details,
        )
        if details.finish_early:
            yield self.finish_request(details)
            return True

        return False

    @tornado.gen.coroutine
    def _read_image(self, details):
        yield Engine.read_image(self, details, details.source_image)
        if details.finish_early:
            yield self.finish_request(details)
            return True
        return False

    @tornado.gen.coroutine
    def _transform_image(self, details):
        # Before transforming the image
        yield Events.trigger(
            Events.Imaging.before_transforming_image,
            self,
            request=self.request,
            details=details,
        )
        if details.finish_early:
            yield self.finish_request(details)
            return True

        yield self._crop_and_resize(details)
        yield self._reorientate(details)
        yield self._trim(details)
        yield self._smart_detect(details)

        yield self._extract_cover(details)
        yield self._manual_crop(details)
        yield self._adjust_dimensions(details)

        if self.context.request.debug:
            yield self._debug()
        else:
            if self.context.request.fit_in:
                yield self._fit_in_resize()
            else:
                yield self._auto_crop()
                yield self._resize()
            yield self._flip()

        # After transforming the image
        yield Events.trigger(
            Events.Imaging.after_transforming_image,
            self,
            request=self.request,
            details=details,
        )
        if details.finish_early:
            yield self.finish_request(details)
            return True

        return False

    @tornado.gen.coroutine
    def _crop_and_resize(self, details):
        req = details.request_parameters
        if req.should_crop:
            yield Engine.crop(self, details, req.crop['left'], req.crop['top'],
                              req.crop['right'], req.crop['bottom'])
        yield Engine.resize(self, details, req.width, req.height)

        if details.transformed_image is None:
            details.transformed_image = details.source_image

    @tornado.gen.coroutine
    def _reorientate(self, details):
        if details.config.RESPECT_ORIENTATION:
            yield Engine.reorientate(self, details)

    @tornado.gen.coroutine
    def _trim(self, details):
        is_gifsicle = (details == 'image/gif' and
                       details.config.USE_GIFSICLE_ENGINE)
        if details.request_parameters.trim is None or not TRIM_ENABLED or is_gifsicle:
            return

        mode, data = yield Engine.get_image_data_as_rgb(self, details)
        size = yield Engine.get_image_size(self, details)
        box = _bounding_box.apply(
            mode, size[0], size[1], details.request_parameters.trim_pos,
            details.request_parameters.trim_tolerance, data)

        if box[2] < box[0] or box[3] < box[1]:
            logger.info(
                "Ignoring trim, there wouldn't be any image left, check the tolerance."
            )
            return

        yield Engine.crop(self, details, box[0], box[1], box[2] + 1, box[3] + 1)
        if details.request_parameters.should_crop:
            details.request_parameters.crop['left'] -= box[0]
            details.request_parameters.crop['top'] -= box[1]
            details.request_parameters.crop['right'] -= box[0]
            details.request_parameters.crop['bottom'] -= box[1]

    @tornado.gen.coroutine
    def _smart_detect(self, details):
        pass

    @tornado.gen.coroutine
    def _serialize_image(self, details):
        yield Engine.serialize(self, details)
        if details.finish_early:
            yield self.finish_request(details)
            return True
        return False
