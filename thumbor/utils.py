#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import logging
from functools import wraps

CONTENT_TYPE = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".png": "image/png",
    ".webp": "image/webp",
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".svg": "image/svg+xml",
    ".tif": "image/tiff",
    ".tiff": "image/tiff",
}

EXTENSION = {
    "image/jpeg": ".jpg",
    "image/gif": ".gif",
    "image/png": ".png",
    "image/webp": ".webp",
    "video/mp4": ".mp4",
    "video/webm": ".webm",
    "image/svg+xml": ".svg",
    "image/tiff": ".tif",
}


logger = logging.getLogger("thumbor")  # pylint: disable=invalid-name


def deprecated(message):
    def decorator_deprecated(func):
        @wraps(func)
        def wrapper_deprecated(*args, **kwargs):
            logger.warning(
                "Deprecated function %s%s",
                func.__name__,
                message,
            )
            return func(*args, **kwargs)

        return wrapper_deprecated

    return decorator_deprecated
