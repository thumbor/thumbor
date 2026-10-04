# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import tornado.web

from thumbor.filters import BaseFilter, filter_method
from thumbor.utils import logger

ALLOWED_FORMATS = ["png", "jpeg", "jpg", "gif", "webp", "avif", "heic", "heif"]
FORMAT_ALIASES = {"jpeg": "jpg", "tiff": "tif", "heif": "heic"}


def normalize_format(image_format):
    image_format = image_format.lower().lstrip(".")
    return FORMAT_ALIASES.get(image_format, image_format)


def get_allowed_conversions(conversions, source_extension):
    if not source_extension:
        return None

    source = normalize_format(source_extension)
    for configured_source, targets in conversions.items():
        if normalize_format(configured_source) == source:
            return {normalize_format(target) for target in targets}

    return None


class Filter(BaseFilter):
    @filter_method(BaseFilter.String)
    async def format(self, file_format):
        self.validate_conversion(file_format)

        if file_format.lower() not in ALLOWED_FORMATS:
            logger.debug("Format not allowed: %s", file_format.lower())
            self.context.request.format = None
        elif (
            file_format.lower() in ("jpeg", "jpg")
            and self.context.request.engine.is_multiple()
        ):
            logger.debug(
                "Format cannot hold multiple frames: %s", file_format.lower()
            )
            self.context.request.format = None
        else:
            logger.debug("Format specified: %s", file_format.lower())
            self.context.request.format = file_format.lower()

    def validate_conversion(self, file_format):
        conversions = self.context.config.FORMAT_FILTER_ALLOWED_CONVERSIONS
        if not conversions:
            return

        source_extension = getattr(self.context.request, "extension", None)
        allowed = get_allowed_conversions(conversions, source_extension)
        if allowed is None:
            return

        requested = file_format.lower()
        if (
            requested in ALLOWED_FORMATS
            and normalize_format(requested) in allowed
        ):
            return

        raise tornado.web.HTTPError(
            400,
            "Conversion from %s to %s is not allowed by "
            "FORMAT_FILTER_ALLOWED_CONVERSIONS",
            source_extension,
            file_format,
        )
