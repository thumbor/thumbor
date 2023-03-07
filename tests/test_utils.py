#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import logging
from shutil import which
from unittest import TestCase, mock

from preggy import expect
import pytest
from PIL import Image, ImageCms

from thumbor.utils import (
    CONTENT_TYPE,
    EXTENSION,
    deprecated,
    logger,
    ensure_srgb,
    get_color_space,
)


class UtilsTestCase(TestCase):
    def setUp(self):
        self.handled = False
        super().setUp()

    @staticmethod
    def test_can_get_content_type():
        expect(CONTENT_TYPE.get(".jpg")).to_equal("image/jpeg")
        expect(CONTENT_TYPE.get(".jpeg")).to_equal("image/jpeg")
        expect(CONTENT_TYPE.get(".gif")).to_equal("image/gif")
        expect(CONTENT_TYPE.get(".png")).to_equal("image/png")
        expect(CONTENT_TYPE.get(".webp")).to_equal("image/webp")
        expect(CONTENT_TYPE.get(".mp4")).to_equal("video/mp4")
        expect(CONTENT_TYPE.get(".webm")).to_equal("video/webm")
        expect(CONTENT_TYPE.get(".svg")).to_equal("image/svg+xml")
        expect(CONTENT_TYPE.get(".tif")).to_equal("image/tiff")
        expect(CONTENT_TYPE.get(".tiff")).to_equal("image/tiff")
        expect(CONTENT_TYPE.get(".avif")).to_equal("image/avif")
        expect(CONTENT_TYPE.get(".heic")).to_equal("image/heif")
        expect(CONTENT_TYPE.get(".heif")).to_equal("image/heif")

    @staticmethod
    def test_can_get_extension():
        expect(EXTENSION.get("image/jpeg")).to_equal(".jpg")
        expect(EXTENSION.get("image/gif")).to_equal(".gif")
        expect(EXTENSION.get("image/png")).to_equal(".png")
        expect(EXTENSION.get("image/webp")).to_equal(".webp")
        expect(EXTENSION.get("video/mp4")).to_equal(".mp4")
        expect(EXTENSION.get("video/webm")).to_equal(".webm")
        expect(EXTENSION.get("image/svg+xml")).to_equal(".svg")
        expect(EXTENSION.get("image/tiff")).to_equal(".tif")
        expect(EXTENSION.get("image/avif")).to_equal(".avif")
        expect(EXTENSION.get("image/heif")).to_equal(".heic")

    @staticmethod
    def test_can_get_logger():
        expect(logger.name).to_equal("thumbor")

    @staticmethod
    def test_deprecated_logs_msg():
        @deprecated("func2")
        def test_func():
            pass

        with mock.patch.object(logger, "warning") as mock_warn:
            test_func()
            mock_warn.assert_called_once_with(
                "Deprecated function %s%s", "test_func", "func2"
            )

    @staticmethod
    def test_can_which_by_path():
        result = which("/bin/ls")
        expect(result).to_include("/bin/ls")

        result = which("/tmp")
        expect(result).to_be_null()

    @staticmethod
    def test_can_which_by_env():
        result = which("ls")
        expect(result).to_include("/bin/ls")

        result = which("invalid-command")
        expect(result).to_be_null()

    @staticmethod
    def test_logger_should_be_instance_of_python_logger():
        expect(logger).to_be_instance_of(logging.Logger)

    @staticmethod
    def test_logger_should_not_be_null():
        expect(logger).not_to_be_null()

    @staticmethod
    def test_logger_should_not_be_an_error():
        expect(logger).not_to_be_an_error()


def test_get_color_space_handles_invalid_icc():
    img = Image.new("RGB", (50, 50), "white")
    img.info["icc_profile"] = b"invalid"
    result = get_color_space(img)
    assert result is None


@mock.patch("thumbor.utils.ImageCms.ImageCmsProfile")
def test_get_color_space_handles_null_xcolor_space(image_cms_profile_mock):
    image_cms_profile_mock.return_value.profile.xcolor_space = None
    img = Image.new("RGB", (50, 50), "white")
    img.info["icc_profile"] = b"wow icc profile with null xcolor_space"
    result = get_color_space(img)
    assert result is None


def test_get_color_space_missing_imagecms_returns_none():
    with mock.patch("thumbor.utils.ImageCms", new=None):
        img = Image.open("tests/fixtures/images/cmyk-icc.jpg")
        assert get_color_space(img) is None


def test_ensure_srgb_handles_invalid_icc():
    img = Image.new("RGB", (50, 50), "white")
    img.info["icc_profile"] = b"invalid"
    retval = ensure_srgb(img)
    assert retval is None


def test_ensure_srgb_missing_imagecms_runtimeerror():
    with mock.patch("thumbor.utils.ImageCms", new=None):
        img = Image.open("tests/fixtures/images/cmyk-icc.jpg")
        with pytest.raises(RuntimeError):
            ensure_srgb(img)


def test_ensure_srgb_keeps_existing_srgb_profile():
    img = Image.new("RGB", (50, 50), "white")
    profile = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB"))
    img.info["icc_profile"] = profile.tobytes()
    retval = ensure_srgb(img)
    assert img is retval


@pytest.mark.parametrize("color_space", ("LAB", "XYZ"))
def test_ensure_srgb_returns_none_for_unsupported_color_space(color_space):
    profile = ImageCms.ImageCmsProfile(ImageCms.createProfile(color_space))
    img = Image.new("RGB", (50, 50), "white")
    img.info["icc_profile"] = profile.tobytes()
    retval = ensure_srgb(img)
    assert retval is None


def test_ensure_srgb_returns_none_for_animated_cmyk():
    img = Image.open("tests/fixtures/images/cmyk-icc.jpg")
    with mock.patch.object(img, "is_animated", new=True, create=True):
        retval = ensure_srgb(img)
        assert retval is None
