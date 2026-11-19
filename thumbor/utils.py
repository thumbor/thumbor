# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import logging
from functools import wraps
from io import BytesIO

from PIL import Image, ImageChops

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

    # Use ImageCms.FLAGS when available and fall back to ImageCms.Flags
    # for compatibility with older and newer PIL versions.
    # This can be refactored once the minimum PIL version is >= 12.

    def _get_flag(flags, name):
        try:
            return flags[name]
        except Exception:
            return getattr(flags, name, 0)

    _FLAGS = getattr(ImageCms, "FLAGS", ImageCms.Flags)

    TRANSFORM_FLAGS = (
        _get_flag(_FLAGS, "NOTCACHE")
        | _get_flag(_FLAGS, "NOTPRECALC")
        | _get_flag(_FLAGS, "BLACKPOINTCOMPENSATION")
        | _get_flag(_FLAGS, "HIGHRESPRECALC")
    )

_PROBE_LEVELS = range(0, 256, 17)

SRGB_PROBES = {
    "GRAY": Image.frombytes("L", (256, 1), bytes(range(256))),
    "RGB": Image.frombytes(
        "RGB",
        (len(_PROBE_LEVELS) ** 3, 1),
        bytes(
            channel
            for red in _PROBE_LEVELS
            for green in _PROBE_LEVELS
            for blue in _PROBE_LEVELS
            for channel in (red, green, blue)
        ),
    ),
}

# Filters leave a gray image in RGB and an RGB one in gray, each with the
# profile it came with
PROFILE_MODES = {
    "GRAY": ("L", "LA", "RGB", "RGBA"),
    "RGB": ("L", "LA", "RGB", "RGBA"),
    "CMYK": ("CMYK",),
}

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
    ".jxl": "image/jxl",
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
    "image/jxl": ".jxl",
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


def _srgb_transform(profile, srgb_profile, source, mode):
    return ImageCms.ImageCmsTransform(
        profile,
        srgb_profile,
        source.mode,
        mode,
        intent=ImageCms.Intent.RELATIVE_COLORIMETRIC,
        flags=TRANSFORM_FLAGS,
    ).apply(source)


def _matches_srgb(profile, color_space, srgb_profile):
    probe = SRGB_PROBES.get(color_space)

    if probe is None:
        return False

    difference = ImageChops.difference(
        probe.convert("RGB"),
        _srgb_transform(profile, srgb_profile, probe, "RGB"),
    )

    # sRGB profiles from different vendors round one level apart at most
    return max(high for _, high in difference.getextrema()) <= 1


def renders_as_srgb(icc):
    """
    Whether an RGB or gray ICC profile renders colors as sRGB does.
    """
    if not icc or ImageCms is None:
        return False

    profile, color_space = get_profile_and_color_space(icc)

    try:
        return _matches_srgb(profile, color_space, DEFAULT_SRGB_PROFILE)
    except (OSError, TypeError, ValueError):
        return False


def convert_to_srgb(img, icc, srgb_profile=None):
    """
    Converts an image from the color space of its ICC profile to sRGB,
    keeping gray images gray and the alpha channel as it is. The image is
    returned unchanged when the profile already renders as sRGB, and the
    result carries no profile. Returns None when the image cannot be
    converted: its mode does not match the color space of the profile, the
    profile cannot be read or used, or ImageCms is not available.
    """
    if ImageCms is None:
        return None

    profile, color_space = get_profile_and_color_space(icc)

    if img.mode not in PROFILE_MODES.get(color_space, ()):
        return None

    if srgb_profile is not None:
        srgb_profile = ImageCms.ImageCmsProfile(srgb_profile)
    else:
        srgb_profile = DEFAULT_SRGB_PROFILE

    try:
        if _matches_srgb(profile, color_space, srgb_profile):
            return img

        logger.debug("Converting from %s to sRGB", color_space)

        if color_space == "CMYK":
            converted = _srgb_transform(profile, srgb_profile, img, "RGB")
        elif color_space == "GRAY":
            # Every color band holds samples in the tone curve of the profile
            bands = [
                _srgb_transform(profile, srgb_profile, band, "RGB").convert(
                    "L"
                )
                for band, name in zip(img.split(), img.getbands())
                if name != "A"
            ]
            converted = (
                bands[0] if len(bands) == 1 else Image.merge("RGB", bands)
            )
        else:
            converted = _srgb_transform(
                profile, srgb_profile, img.convert("RGB"), "RGB"
            )

            if img.mode in ("L", "LA"):
                converted = converted.convert("L")

        if "A" in img.getbands():
            converted.putalpha(img.getchannel("A"))
    except (OSError, TypeError, ValueError) as error:
        # lcms opens profiles it cannot use as a source, a device link or
        # one with tags missing among them
        logger.debug("Cannot convert to sRGB: %s", error)
        return None

    converted.info = {
        key: value for key, value in img.info.items() if key != "icc_profile"
    }

    return converted
