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

import math

import tornado.web
import tornado.gen
import magic

import thumbor.context
from thumbor.lifecycle import Events
from thumbor.handlers.request_details import RequestDetails
from thumbor import Engine
from thumbor.utils import logger
from thumbor.point import FocalPoint

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

        yield self._reorientate(details)
        yield self._trim(details)
        yield self._smart_detect(details)

        yield self._extract_cover(details)
        yield self._manual_crop(details)
        yield self._adjust_dimensions(details)
        yield self._adjust_focal_points(details)

        if details.request_parameters.debug:
            yield self._debug()
        else:
            if details.request_parameters.fit_in:
                yield self._fit_in_resize()
            else:
                yield self._auto_crop(details)
                yield self._resize(details)
            yield self._flip(details)

        if details.transformed_image is None:
            details.transformed_image = details.source_image

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
    def _extract_cover(self, details):
        if details.mimetype == 'image/gif' and 'cover()' in details.request_parameters.filters:
            pass  # TODO: implement this

    @tornado.gen.coroutine
    def _manual_crop(self, details):
        if details.request_parameters.should_crop:
            def limit(dimension, maximum):
                return min(max(dimension, 0), maximum)

            source_width, source_height = yield Engine.get_image_size(self, details)
            crop = details.request_parameters.crop

            crop['left'] = limit(crop['left'], source_width)
            crop['top'] = limit(crop['top'], source_height)
            crop['right'] = limit(crop['right'], source_width)
            crop['bottom'] = limit(crop['bottom'], source_height)

            if crop['left'] >= crop['right'] or crop['top'] >= crop['bottom']:
                details.request_parameters.should_crop = False
                crop['left'] = crop['right'] = crop['top'] = crop['bottom'] = 0
                return

            yield Engine.crop(
                self, details,
                crop['left'], crop['top'],
                crop['right'], crop['bottom'],
            )

    @tornado.gen.coroutine
    def _adjust_dimensions(self, details):
        source_width, source_height = yield Engine.get_image_size(self, details)
        source_width = float(source_width)
        source_height = float(source_height)

        if not details.request_parameters.width and not details.request_parameters.height:
            details.target_width = source_width
            details.target_height = source_height
        else:
            if details.request_parameters.width:
                if details.request_parameters.width == "orig":
                    details.target_width = source_width
                else:
                    details.target_width = float(details.request_parameters.width)
            else:
                details.target_width = yield Engine.get_proportional_width(self, details, details.request_parameters.height)

            if details.request_parameters.height:
                if details.request_parameters.height == "orig":
                    details.target_height = source_height
                else:
                    details.target_height = float(details.request_parameters.height)
            else:
                details.target_height = yield Engine.get_proportional_height(self, details, details.request_parameters.width)

    @tornado.gen.coroutine
    def _adjust_focal_points(self, details):
        source_width, source_height = yield Engine.get_image_size(self, details)

        details.focal_points = None

        if details.request_parameters.focal_points:
            if details.request_parameters.should_crop:
                details.focal_points = []
                crop = details.request_parameters.crop
                for point in details.request_parameters.focal_points:
                    if point.x < crop['left'] or point.x > crop['right'] or point.y < crop['top'] or point.y > crop['bottom']:
                        continue
                    point.x -= crop['left'] or 0
                    point.y -= crop['top'] or 0
                    details.focal_points.append(point)
            else:
                details.focal_points = details.request_parameters.focal_points

        if not details.focal_points:
            details.focal_points = [
                FocalPoint.from_alignment(details.request_parameters.halign,
                                          details.request_parameters.valign,
                                          source_width,
                                          source_height)
            ]

        yield Engine.focus(self, details)

    @tornado.gen.coroutine
    def _auto_crop(self, details):
        source_width, source_height = yield Engine.get_image_size(self, details)

        target_height = details.target_height or 1
        target_width = details.target_width or 1

        source_ratio = round(float(source_width) / source_height, 2)
        target_ratio = round(float(target_width) / target_height, 2)

        if source_ratio == target_ratio:
            return

        focal_x, focal_y = self._get_center_of_mass(details)

        if details.target_width / source_width > details.target_height / source_height:
            crop_width = source_width
            crop_height = int(round(source_width * details.target_height / target_width, 0))
        else:
            crop_width = int(round(math.ceil(details.target_width * source_height / target_height), 0))
            crop_height = source_height

        crop_left = int(round(min(max(focal_x - (crop_width / 2), 0.0), source_width - crop_width)))
        crop_right = min(crop_left + crop_width, source_width)

        crop_top = int(round(min(max(focal_y - (crop_height / 2), 0.0), source_height - crop_height)))
        crop_bottom = min(crop_top + crop_height, source_height)

        yield Engine.crop(self, details, crop_left, crop_top, crop_right, crop_bottom)

    def _get_center_of_mass(self, details):
        total_weight = 0.0
        total_x = 0.0
        total_y = 0.0

        for focal_point in details.focal_points:
            total_weight += focal_point.weight

            total_x += focal_point.x * focal_point.weight
            total_y += focal_point.y * focal_point.weight

        x = total_x / total_weight
        y = total_y / total_weight

        return x, y

    @tornado.gen.coroutine
    def _resize(self, details):
        source_width, source_height = yield Engine.get_image_size(self, details)
        if details.target_width == source_width and details.target_height == source_height:
            return
        yield Engine.resize(self, details, details.target_width or 1, details.target_height or 1)  # avoiding 0px images

    @tornado.gen.coroutine
    def _flip(self, details):
        if details.request_parameters.horizontal_flip:
            yield Engine.flip_horizontally(self, details)
        if details.request_parameters.vertical_flip:
            yield Engine.flip_vertically(self, details)

    @tornado.gen.coroutine
    def _fit_in_resize(self, details):
        source_width, source_height = yield Engine.get_image_size(self, details)

        # invert width and height if image orientation is not the same as request orientation and need adaptive
        if details.request_parameters.adaptive and (
            (source_width - source_height < 0 and details.target_width - details.target_height > 0) or
            (source_width - source_height > 0 and details.target_width - details.target_height < 0)
        ):
            tmp = details.request_parameters.width
            details.request_parameters.width = details.request_parameters.height
            details.request_parameters.height = tmp
            tmp = details.target_width
            details.target_width = details.target_height
            details.target_height = tmp

        sign = 1
        if details.request_parameters.full:
            sign = -1

        if sign == 1 and details.target_width >= source_width and details.target_height >= source_height:
            return

        if source_width / details.target_width * sign >= source_height / details.target_height * sign:
            resize_height = round(source_height * details.target_width / source_width)
            resize_width = details.target_width
        else:
            resize_height = details.target_height
            resize_width = round(source_width * details.target_height / source_height)

        # ensure that filter should work on the real image size and not on the request
        # size which might be smaller than the resized image in case `full-fit-in` is
        # being used
        requested_width = source_width if details.request_parameters.width == 'orig' else details.request_parameters.width
        requested_height = source_height if details.request_parameters.height == 'orig' else details.request_parameters.height
        details.request_parameters.width = int(max(requested_width, resize_width))
        details.request_parameters.height = int(max(requested_height, resize_height))

        yield Engine.resize(self, details, resize_width, resize_height)

    @tornado.gen.coroutine
    def debug(self, details):
        if not details.request_parameters.focal_points:
            return

        for point in details.request_parameters.focal_points:
            if point.width <= 1:
                point.width = 10
            if point.height <= 1:
                point.height = 10
            yield Engine.draw_rectangle(
                self,
                details,
                int(point.x - (point.width / 2)),
                int(point.y - (point.height / 2)),
                point.width,
                point.height,
            )

    @tornado.gen.coroutine
    def _serialize_image(self, details):
        yield Engine.serialize(self, details)
        if details.finish_early:
            yield self.finish_request(details)
            return True
        return False
