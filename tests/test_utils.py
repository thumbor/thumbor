# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import logging
from shutil import which
from unittest import TestCase, mock

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
        assert CONTENT_TYPE.get(".jpg") == "image/jpeg"
        assert CONTENT_TYPE.get(".jpeg") == "image/jpeg"
        assert CONTENT_TYPE.get(".gif") == "image/gif"
        assert CONTENT_TYPE.get(".png") == "image/png"
        assert CONTENT_TYPE.get(".webp") == "image/webp"
        assert CONTENT_TYPE.get(".mp4") == "video/mp4"
        assert CONTENT_TYPE.get(".webm") == "video/webm"
        assert CONTENT_TYPE.get(".svg") == "image/svg+xml"
        assert CONTENT_TYPE.get(".tif") == "image/tiff"
        assert CONTENT_TYPE.get(".tiff") == "image/tiff"
        assert CONTENT_TYPE.get(".avif") == "image/avif"
        assert CONTENT_TYPE.get(".heic") == "image/heif"
        assert CONTENT_TYPE.get(".heif") == "image/heif"

    @staticmethod
    def test_can_get_extension():
        assert EXTENSION.get("image/jpeg") == ".jpg"
        assert EXTENSION.get("image/gif") == ".gif"
        assert EXTENSION.get("image/png") == ".png"
        assert EXTENSION.get("image/webp") == ".webp"
        assert EXTENSION.get("video/mp4") == ".mp4"
        assert EXTENSION.get("video/webm") == ".webm"
        assert EXTENSION.get("image/svg+xml") == ".svg"
        assert EXTENSION.get("image/tiff") == ".tif"
        assert EXTENSION.get("image/avif") == ".avif"
        assert EXTENSION.get("image/heif") == ".heic"

    @staticmethod
    def test_can_get_logger():
        assert logger.name == "thumbor"

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
        assert "/bin/ls" in result

        result = which("/tmp")
        assert result is None

    @staticmethod
    def test_can_which_by_env():
        result = which("ls")
        assert "/bin/ls" in result

        result = which("invalid-command")
        assert result is None

    @staticmethod
    def test_logger_should_be_instance_of_python_logger():
        assert isinstance(logger, logging.Logger)

    @staticmethod
    def test_logger_should_not_be_null():
        assert logger is not None

    @staticmethod
    def test_logger_should_not_be_an_error():
        assert not isinstance(logger, Exception)


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
