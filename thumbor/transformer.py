#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import math
import sys

from thumbor.point import FocalPoint
from thumbor.utils import logger

TRIM_ENABLED = True
try:
    from thumbor.ext.filters import _bounding_box
except ImportError:
    logger.warning("Error importing bounding_box filter, trimming won't work")
    TRIM_ENABLED = False


class Transformer:
    def __init__(self, context):
        self.context = context
        self.engine = self.context.request.engine
        self.focal_points = None
        self.target_height = None
        self.target_width = None

    async def transform(self):
        if self.context.config.RESPECT_ORIENTATION:
            self.engine.reorientate()
        await self.trim()
        await self.smart_detect()
        await self.do_image_operations()

    async def trim(self):
        is_gifsicle = (
            self.context.request.engine.extension == ".gif"
            and self.context.config.USE_GIFSICLE_ENGINE
        )
        if (
            self.context.request.trim is None
            or not TRIM_ENABLED
            or is_gifsicle
        ):
            return

        mode, data = self.engine.image_data_as_rgb()
        box = _bounding_box.apply(
            mode,
            self.engine.size[0],
            self.engine.size[1],
            self.context.request.trim_pos,
            self.context.request.trim_tolerance,
            data,
        )

        if box[2] < box[0] or box[3] < box[1]:
            logger.warning(
                "Ignoring trim, there wouldn't be any image "
                "left, check the tolerance."
            )
            return

        self.engine.crop(box[0], box[1], box[2] + 1, box[3] + 1)
        if self.context.request.should_crop:
            self.context.request.crop["left"] -= box[0]
            self.context.request.crop["top"] -= box[1]
            self.context.request.crop["right"] -= box[0]
            self.context.request.crop["bottom"] -= box[1]

    def _calculate_target_dimensions(self):
        source_width, source_height = self.engine.size
        source_width = float(source_width)
        source_height = float(source_height)

        if not self.context.request.width and not self.context.request.height:
            self.target_width = source_width
            self.target_height = source_height
        else:
            if self.context.request.width:
                if self.context.request.width == "orig":
                    self.target_width = source_width
                else:
                    self.target_width = float(self.context.request.width)
            else:
                self.target_width = self.engine.get_proportional_width(
                    self.context.request.height
                )

            if self.context.request.height:
                if self.context.request.height == "orig":
                    self.target_height = source_height
                else:
                    self.target_height = float(self.context.request.height)
            else:
                self.target_height = self.engine.get_proportional_height(
                    self.context.request.width
                )

    def get_target_dimensions(self):
        """
        Returns the target dimensions and calculates them if necessary.
        The target dimensions are display independent.
        :return: Target dimensions as a tuple (width, height)
        :rtype: (int, int)
        """
        if self.target_height is None:
            self._calculate_target_dimensions()
        return int(self.target_width), int(self.target_height)

    def adjust_focal_points(self):
        source_width, source_height = self.engine.size

        self.focal_points = None

        if self.context.request.focal_points:
            if self.context.request.should_crop:
                self.focal_points = []
                crop = self.context.request.crop
                for point in self.context.request.focal_points:
                    if (
                        point.x < crop["left"]
                        or point.x > crop["right"]
                        or point.y < crop["top"]
                        or point.y > crop["bottom"]
                    ):
                        continue
                    point.x -= crop["left"] or 0
                    point.y -= crop["top"] or 0
                    self.focal_points.append(point)
            else:
                self.focal_points = self.context.request.focal_points

        if not self.focal_points:
            self.focal_points = [
                FocalPoint.from_alignment(
                    self.context.request.halign,
                    self.context.request.valign,
                    source_width,
                    source_height,
                )
            ]

        self.engine.focus(self.focal_points)

    @property
    def smart_storage_key(self):
        return self.context.request.image_url

    async def smart_detect(self):
        is_gifsicle = (
            self.context.request.engine.extension == ".gif"
            and self.context.config.USE_GIFSICLE_ENGINE
        )
        if (
            not (self.context.modules.detectors and self.context.request.smart)
        ) or is_gifsicle:
            return

        try:
            await self.do_smart_detection()
        except Exception:  # pylint: disable=broad-except
            if not self.context.config.IGNORE_SMART_ERRORS:
                raise

            logger.exception("Ignored error during smart detection")
            if self.context.config.USE_CUSTOM_ERROR_HANDLING:
                self.context.modules.importer.error_handler.handle_error(
                    context=self.context,
                    handler=self.context.request_handler,
                    exception=sys.exc_info(),
                )

            self.context.request.prevent_result_storage = True
            self.context.request.detection_error = True

    async def do_smart_detection(self):
        focal_points = await self.context.modules.storage.get_detector_data(
            self.smart_storage_key
        )
        points_from_storage = focal_points is not None
        if focal_points is None:
            detectors = self.context.modules.detectors
            focal_points = await detectors[0](
                self.context, index=0, detectors=detectors
            ).detect()

        if focal_points is not None:
            for point in focal_points:
                self.context.request.focal_points.append(
                    FocalPoint.from_dict(point)
                )

        if (
            self.context.request.focal_points
            and self.context.modules.storage
            and not points_from_storage
        ):
            storage = self.context.modules.storage
            points = []
            for point in self.context.request.focal_points:
                points.append(point.to_dict())

            await storage.put_detector_data(self.smart_storage_key, points)

    async def do_image_operations(self):
        """
        If ENGINE_THREADPOOL_SIZE > 0, this will schedule the image operations
        into a threadpool.  If not, it just executes them synchronously.

        The actual work happens in self.img_operation_worker
        """
        await self.context.thread_pool.queue(
            operation=self.img_operation_worker,
        )

    def img_operation_worker(self):
        if (
            self.context.request.engine.extension == ".gif"
            and "cover()" in self.context.request.filters
        ):
            self.extract_cover()

        self.manual_crop()
        self._calculate_target_dimensions()
        self.adjust_focal_points()

        if self.context.request.debug:
            self.debug()
        else:
            if self.context.request.fit_in:
                self.fit_in_resize()
            else:
                if not self.context.request.stretch:
                    self.auto_crop()
                self.resize()
            self.flip()

    def extract_cover(self):
        self.engine.extract_cover()

    def manual_crop(self):
        if self.context.request.should_crop:

            def limit(dimension, maximum):
                return min(max(dimension, 0), maximum)

            source_width, source_height = self.engine.size
            crop = self.context.request.crop

            crop["left"] = limit(crop["left"], source_width)
            crop["top"] = limit(crop["top"], source_height)
            crop["right"] = limit(crop["right"], source_width)
            crop["bottom"] = limit(crop["bottom"], source_height)

            if crop["left"] >= crop["right"] or crop["top"] >= crop["bottom"]:
                self.context.request.should_crop = False
                crop["left"] = crop["right"] = crop["top"] = crop["bottom"] = 0
                return

            self.engine.crop(
                crop["left"], crop["top"], crop["right"], crop["bottom"]
            )

    def auto_crop(self):
        source_width, source_height = self.engine.size

        target_height = self.target_height or 1
        target_width = self.target_width or 1

        source_ratio = round(source_width / source_height, 2)
        target_ratio = round(target_width / target_height, 2)

        if source_ratio == target_ratio:
            return

        focal_x, focal_y = self.get_center_of_mass()

        if (
            self.target_width / source_width
            > self.target_height / source_height
        ):
            crop_width = source_width
            crop_height = int(
                round(source_width * self.target_height / target_width, 0)
            )
        else:
            crop_width = int(
                round(
                    math.ceil(
                        self.target_width * source_height / target_height
                    ),
                    0,
                )
            )
            crop_height = source_height

        crop_left = int(
            round(
                min(
                    max(focal_x - (crop_width / 2), 0.0),
                    source_width - crop_width,
                )
            )
        )
        crop_right = min(crop_left + crop_width, source_width)

        crop_top = int(
            round(
                min(
                    max(focal_y - (crop_height / 2), 0.0),
                    source_height - crop_height,
                )
            )
        )
        crop_bottom = min(crop_top + crop_height, source_height)

        self.engine.crop(crop_left, crop_top, crop_right, crop_bottom)

    def flip(self):
        if self.context.request.horizontal_flip:
            self.engine.flip_horizontally()
        if self.context.request.vertical_flip:
            self.engine.flip_vertically()

    def get_center_of_mass(self):
        total_weight = 0.0
        total_x = 0.0
        total_y = 0.0

        for focal_point in self.focal_points:
            total_weight += focal_point.weight

            total_x += focal_point.x * focal_point.weight
            total_y += focal_point.y * focal_point.weight

        avg_x = total_x // total_weight
        avg_y = total_y // total_weight

        return avg_x, avg_y

    def resize(self):
        source_width, source_height = self.engine.size
        if (
            self.target_width == source_width
            and self.target_height == source_height
        ):
            return
        self.engine.resize(
            self.target_width or 1, self.target_height or 1
        )  # avoiding 0px images

    def fit_in_resize(self):
        source_width, source_height = self.engine.size

        # invert width and height if image orientation is not the
        # same as request orientation and need adaptive
        if self.context.request.adaptive and (
            (
                source_width < source_height
                and self.target_width > self.target_height
            )
            or (
                source_width > source_height
                and self.target_width < self.target_height
            )
        ):
            tmp = self.context.request.width
            self.context.request.width = self.context.request.height
            self.context.request.height = tmp
            tmp = self.target_width
            self.target_width = self.target_height
            self.target_height = tmp

        sign = 1
        if self.context.request.full:
            sign = -1

        if (
            sign == 1
            and self.target_width >= source_width
            and self.target_height >= source_height
        ):
            return

        # add 1e-5 to get .5 rounding up in Python3 as it was in Python2
        if (
            source_width / self.target_width * sign
            >= source_height / self.target_height * sign
        ):
            resize_height = round(
                source_height * self.target_width / source_width + 1e-5
            )
            resize_width = self.target_width
        else:
            resize_height = self.target_height
            resize_width = round(
                source_width * self.target_height / source_height + 1e-5
            )

        # ensure that filter should work on the real image size
        # and not on the request size which might be smaller than the
        # resized image in case `full-fit-in` is being used
        requested_width = (
            source_width
            if self.context.request.width == "orig"
            else self.context.request.width
        )
        requested_height = (
            source_height
            if self.context.request.height == "orig"
            else self.context.request.height
        )
        self.context.request.width = int(max(requested_width, resize_width))
        self.context.request.height = int(max(requested_height, resize_height))

        self.engine.resize(resize_width, resize_height)

    def debug(self):
        if not self.context.request.focal_points:
            return

        for point in self.context.request.focal_points:
            if point.width <= 1:
                point.width = 10
            if point.height <= 1:
                point.height = 10
            self.engine.draw_rectangle(
                point.x - (point.width // 2),
                point.y - (point.height // 2),
                point.width,
                point.height,
            )
