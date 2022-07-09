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


def is_animated_gif(data):
    if data[:6] not in [b"GIF87a", b"GIF89a"]:
        return False
    i = 10  # skip header
    frames = 0

    def skip_color_table(i, flags):
        if flags & 0x80:
            i += 3 << ((flags & 7) + 1)

        return i

    flags = data[i]
    i = skip_color_table(i + 3, flags)

    while frames < 2:
        block = data[i : i + 1]  # NOQA
        i += 1

        if block == b"\x3B":
            break

        if block == b"\x21":
            i += 1
        elif block == b"\x2C":
            frames += 1
            i += 8
            i = skip_color_table(i + 1, data[i])
            i += 1
        else:
            return False

        while True:
            j = data[i]
            i += 1

            if not j:
                break
            i += j

    return frames > 1
