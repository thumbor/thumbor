# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2025 globo.com thumbor@googlegroups.com

from thumbor.utils import logger

DEFAULT_AUTO_IMAGE_FORMAT_PREFERENCE = ("webp", "avif", "jpg", "heif", "png")
VALID_AUTO_IMAGE_FORMATS = frozenset(DEFAULT_AUTO_IMAGE_FORMAT_PREFERENCE)
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


def _get_raw_auto_image_format_preference(config):
    return tuple(getattr(config, "AUTO_IMAGE_FORMAT_PREFERENCE", ()) or ())


def has_auto_image_format_preference(config):
    return bool(get_normalized_auto_image_format_preference(config))


def get_normalized_auto_image_format_preference(config):
    raw_preference = _get_raw_auto_image_format_preference(config)
    cached_preference = getattr(
        config,
        "_AUTO_IMAGE_FORMAT_PREFERENCE_CACHE",
        None,
    )

    if cached_preference is None or cached_preference[0] != raw_preference:
        normalized_preference = []
        invalid_formats = []
        seen_formats = set()

        for image_format in raw_preference:
            if not isinstance(image_format, str):
                invalid_formats.append(image_format)
                continue

            normalized_format = image_format.strip().lower()

            if normalized_format not in VALID_AUTO_IMAGE_FORMATS:
                invalid_formats.append(image_format)
                continue

            if normalized_format in seen_formats:
                continue

            seen_formats.add(normalized_format)
            normalized_preference.append(normalized_format)

        if invalid_formats:
            logger.warning(
                "Ignoring invalid AUTO_IMAGE_FORMAT_PREFERENCE values: %r. "
                "Valid formats are: %s.",
                invalid_formats,
                ", ".join(DEFAULT_AUTO_IMAGE_FORMAT_PREFERENCE),
            )

        cached_preference = (
            raw_preference,
            tuple(normalized_preference),
        )
        setattr(
            config,
            "_AUTO_IMAGE_FORMAT_PREFERENCE_CACHE",
            cached_preference,
        )

    return cached_preference[1]


def get_active_auto_image_formats(config):
    if has_auto_image_format_preference(config):
        return get_normalized_auto_image_format_preference(config)

    active_formats = []

    for image_format in DEFAULT_AUTO_IMAGE_FORMAT_PREFERENCE:
        config_flag = AUTO_IMAGE_FORMAT_CONFIG_FLAGS[image_format]

        if getattr(config, config_flag, False):
            active_formats.append(image_format)

    return tuple(active_formats)


def requires_auto_image_format_cache_isolation(config):
    """Return whether legacy ``default``/``auto_webp`` keys are unsafe."""
    if has_auto_image_format_preference(config):
        return True

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
    preference_enabled = has_auto_image_format_preference(config)
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
        policy = "preference" if preference_enabled else "flags"
        fallback = (
            "png_to_jpg"
            if getattr(config, "AUTO_PNG_TO_JPG", False)
            else "preserve"
        )
        variant = "-".join(accepted_formats) or "default"
        return (
            f"{AUTO_IMAGE_FORMAT_CACHE_KEY_PREFIX}_{policy}_"
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
