# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2025 globo.com thumbor@googlegroups.com

DEFAULT_AUTO_IMAGE_FORMAT_PREFERENCE = ("webp", "avif", "jpg", "heif", "png")
VALID_AUTO_IMAGE_FORMATS = frozenset(DEFAULT_AUTO_IMAGE_FORMAT_PREFERENCE)

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
    return bool(_get_raw_auto_image_format_preference(config))


def get_normalized_auto_image_format_preference(config):
    raw_preference = _get_raw_auto_image_format_preference(config)

    if (
        getattr(config, "_AUTO_IMAGE_FORMAT_PREFERENCE_CACHE_KEY", None)
        != raw_preference
    ):
        normalized_preference = []
        seen_formats = set()

        for image_format in raw_preference:
            if not isinstance(image_format, str):
                continue

            normalized_format = image_format.strip().lower()

            if (
                normalized_format not in VALID_AUTO_IMAGE_FORMATS
                or normalized_format in seen_formats
            ):
                continue

            seen_formats.add(normalized_format)
            normalized_preference.append(normalized_format)

        setattr(
            config,
            "_AUTO_IMAGE_FORMAT_PREFERENCE_CACHE_KEY",
            raw_preference,
        )
        setattr(
            config,
            "_AUTO_IMAGE_FORMAT_PREFERENCE_NORMALIZED",
            tuple(normalized_preference),
        )

    return getattr(config, "_AUTO_IMAGE_FORMAT_PREFERENCE_NORMALIZED", ())


def get_active_auto_image_formats(config):
    if has_auto_image_format_preference(config):
        return get_normalized_auto_image_format_preference(config)

    active_formats = []

    for image_format in DEFAULT_AUTO_IMAGE_FORMAT_PREFERENCE:
        config_flag = AUTO_IMAGE_FORMAT_CONFIG_FLAGS[image_format]

        if getattr(config, config_flag, False):
            active_formats.append(image_format)

    return tuple(active_formats)


def get_auto_image_format_cache_key(config, request):
    active_formats = get_active_auto_image_formats(config)

    if not active_formats:
        return None

    accepted_formats = []

    for image_format in active_formats:
        accept_attr = AUTO_IMAGE_FORMAT_ACCEPT_ATTRS[image_format]

        if getattr(request, accept_attr, False):
            accepted_formats.append(image_format)

    if not accepted_formats:
        return None

    return "auto_" + "-".join(accepted_formats)
