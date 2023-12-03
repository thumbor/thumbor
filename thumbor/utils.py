#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import logging
from functools import wraps
from io import BytesIO
from PIL import Image

try:
    from PIL import ImageCms  # pylint: disable=ungrouped-imports
except ImportError:
    ImageCms = None
    DEFAULT_SRGB_PROFILE = None
    TRANSFORM_FLAGS = 0
else:
    DEFAULT_SRGB_PROFILE = ImageCms.ImageCmsProfile(
        ImageCms.createProfile("sRGB")
    )
    TRANSFORM_FLAGS = (
        ImageCms.FLAGS["NOTCACHE"]
        | ImageCms.FLAGS["NOTPRECALC"]
        | ImageCms.FLAGS["BLACKPOINTCOMPENSATION"]
        | ImageCms.FLAGS["HIGHRESPRECALC"]
    )


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
    ".avif": "image/avif",
    ".heic": "image/heif",
    ".heif": "image/heif",
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
    "image/avif": ".avif",
    "image/heif": ".heic",
}


logger = logging.getLogger("thumbor")


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


def get_profile_and_color_space(icc):
    with BytesIO(icc) as buf:
        try:
            profile = ImageCms.ImageCmsProfile(buf)
            return profile, profile.profile.xcolor_space.strip()
        except (AttributeError, OSError, TypeError, ValueError):
            return None, None


def get_color_space(img):
    icc = img.info.get("icc_profile")
    if not icc:
        return "RGB"

    if ImageCms is None:
        return None

    _, color_space = get_profile_and_color_space(icc)
    return color_space


def ensure_srgb(img, srgb_profile=None):
    """
    Ensures that an image either has no ICC profile (and so is implicitly
    sRGB) or has an sRGB color profile. If the image is sRGB, it is returned
    unchanged. If it has a CMYK or Gray color profile, this function will
    return an image converted to sRGB. Any color profiles in other color
    spaces will return None.
    """
    img_info = dict(img.info)
    icc = img_info.pop("icc_profile", None)
    if not icc:
        return img

    if ImageCms is None:
        raise RuntimeError("ImageCms is required for color profile utilities")

    if srgb_profile is not None:
        srgb_profile = ImageCms.ImageCmsProfile(srgb_profile)
    else:
        srgb_profile = DEFAULT_SRGB_PROFILE

    orig_profile, color_space = get_profile_and_color_space(icc)

    if not color_space:
        return None

    if color_space == "RGB":
        logger.debug("Returning img (RGB)")
        return img

    if color_space not in ("GRAY", "CMYK"):
        # Other color spaces are rare, but best not to try to convert them.
        # Upstream understands a None return as meaning it should not
        # use it for the target encoder.
        logger.debug("Cannot convert to sRGB; color space = %s", color_space)
        return None

    # Probably not possible to have an animated image with CMYK or GRAY icc
    # profile, but best leave it alone if we have one
    if getattr(img, "is_animated", False):
        return None

    if color_space == "GRAY":
        pil_mode = "L"
    else:
        pil_mode = "CMYK"

    logger.debug("Converting from %s to sRGB", color_space)

    transform = ImageCms.ImageCmsTransform(
        orig_profile,
        srgb_profile,
        pil_mode,
        "RGBA",
        intent=ImageCms.Intent.RELATIVE_COLORIMETRIC,
        flags=TRANSFORM_FLAGS,
    )

    src_im = Image.new(pil_mode, img.size, "white")
    src_im.paste(img)

    dst_im = Image.new("RGBA", img.size, "white")
    dst_im.info = img_info
    dst_im = transform.apply(src_im, dst_im)
    dst_im = dst_im.convert("RGB")
    dst_im.info = img_info
    return dst_im
