# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2025 globo.com thumbor@googlegroups.com

DEFAULT_AUTO_IMAGE_FORMAT_PREFERENCE = ("webp", "avif", "jpg", "heif", "png")
AUTO_IMAGE_FORMAT_CACHE_KEY_PREFIX = "auto_format_v1"

AUTO_IMAGE_FORMAT_CONFIG_FLAGS = {
    "webp": "AUTO_WEBP",
    "avif": "AUTO_AVIF",
    "jpg": "AUTO_JPG",
    "heif": "AUTO_HEIF",
    "png": "AUTO_PNG",
}

AUTO_IMAGE_FORMAT_ACCEPT_ATTRS = {
    "webp": "accepts_webp",
    "avif": "accepts_avif",
    "jpg": "accepts_jpeg",
    "heif": "accepts_heif",
    "png": "accepts_png",
}


def get_active_auto_image_formats(config):
    active_formats = []

    for image_format in DEFAULT_AUTO_IMAGE_FORMAT_PREFERENCE:
        config_flag = AUTO_IMAGE_FORMAT_CONFIG_FLAGS[image_format]

        if getattr(config, config_flag, False):
            active_formats.append(image_format)

    return tuple(active_formats)


def requires_auto_image_format_cache_isolation(config):
    """Return whether legacy ``default``/``auto_webp`` keys are unsafe."""
    return getattr(config, "AUTO_PNG_TO_JPG", False) or any(
        getattr(config, AUTO_IMAGE_FORMAT_CONFIG_FLAGS[image_format], False)
        for image_format in DEFAULT_AUTO_IMAGE_FORMAT_PREFERENCE
        if image_format != "webp"
    )


def get_auto_image_format_cache_key(config, request):
    """Return the cache variant for an auto-format request.

    Result storage implementations can use this helper to keep responses for
    different ``Accept`` capabilities in separate cache namespaces.
    """
    active_formats = get_active_auto_image_formats(config)
    cache_isolation_required = requires_auto_image_format_cache_isolation(
        config
    )

    if not active_formats and not cache_isolation_required:
        return None

    accepted_formats = []

    for image_format in active_formats:
        accept_attr = AUTO_IMAGE_FORMAT_ACCEPT_ATTRS[image_format]

        if getattr(request, accept_attr, False):
            accepted_formats.append(image_format)

    if cache_isolation_required:
        fallback = (
            "png_to_jpg"
            if getattr(config, "AUTO_PNG_TO_JPG", False)
            else "preserve"
        )
        variant = "-".join(accepted_formats) or "default"
        return (
            f"{AUTO_IMAGE_FORMAT_CACHE_KEY_PREFIX}_flags_"
            f"{fallback}_{variant}"
        )

    if not accepted_formats:
        return None

    return "auto_" + "-".join(accepted_formats)


def get_legacy_auto_image_format_cache_key(config, request):
    """Return the cache variant used by the legacy ``v2`` file layout."""
    if getattr(config, "AUTO_WEBP", False) and getattr(
        request, "accepts_webp", False
    ):
        return "auto_webp"

    return None
