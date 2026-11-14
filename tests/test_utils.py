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
    convert_to_srgb,
    deprecated,
    ensure_srgb,
    get_color_space,
    logger,
    renders_as_srgb,
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


def linear_p3_image(mode="RGB"):
    image = Image.open("tests/fixtures/images/image-linear-p3.jpg")

    return image.convert(mode), image.info["icc_profile"]


def srgb_icc():
    return ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()


def test_convert_to_srgb_converts_an_rgb_profile():
    img, icc = linear_p3_image()
    img.info["exif"] = b"exif"

    converted = convert_to_srgb(img, icc)

    assert converted.mode == "RGB"
    assert converted.tobytes() != img.tobytes()
    assert converted.info == {
        key: value for key, value in img.info.items() if key != "icc_profile"
    }
    assert "exif" in converted.info


def test_convert_to_srgb_keeps_the_alpha_channel():
    img, icc = linear_p3_image("RGBA")
    img.putalpha(Image.linear_gradient("L").resize(img.size))

    converted = convert_to_srgb(img, icc)

    assert converted.mode == "RGBA"
    assert converted.getchannel("A").tobytes() == (
        img.getchannel("A").tobytes()
    )
    assert converted.convert("RGB").tobytes() != img.convert("RGB").tobytes()


def test_convert_to_srgb_returns_an_srgb_image_unchanged():
    img = Image.effect_noise((16, 16), 64).convert("RGB")

    assert convert_to_srgb(img, srgb_icc()) is img


def test_convert_to_srgb_keeps_a_gray_image_gray():
    img = Image.open("tests/fixtures/images/grayscale-icc.jpg")
    icc = img.info["icc_profile"]

    converted = convert_to_srgb(img, icc)

    assert converted.mode == "L"
    assert converted.tobytes() != img.tobytes()

    with_alpha = img.convert("LA")
    with_alpha.putalpha(Image.linear_gradient("L").resize(img.size))

    converted = convert_to_srgb(with_alpha, icc)

    assert converted.mode == "LA"
    assert converted.getchannel("A").tobytes() == (
        with_alpha.getchannel("A").tobytes()
    )


def test_convert_to_srgb_converts_cmyk_to_rgb():
    img = Image.open("tests/fixtures/images/cmyk-icc.jpg")

    converted = convert_to_srgb(img, img.info["icc_profile"])

    assert converted.mode == "RGB"
    assert converted.tobytes() != img.convert("RGB").tobytes()


def test_convert_to_srgb_uses_the_given_srgb_profile(tmp_path):
    img, icc = linear_p3_image()
    profile_path = tmp_path / "target.icc"
    profile_path.write_bytes(icc)

    assert convert_to_srgb(img, icc) is not img
    assert convert_to_srgb(img, icc, str(profile_path)) is img


def test_convert_to_srgb_converts_a_gray_image_with_an_rgb_profile():
    img, icc = linear_p3_image("L")

    converted = convert_to_srgb(img, icc)

    assert converted.mode == "L"
    assert converted.tobytes() != img.tobytes()

    with_alpha = img.convert("LA")
    with_alpha.putalpha(Image.linear_gradient("L").resize(img.size))

    converted = convert_to_srgb(with_alpha, icc)

    assert converted.mode == "LA"
    assert converted.getchannel("A").tobytes() == (
        with_alpha.getchannel("A").tobytes()
    )


def test_convert_to_srgb_converts_an_rgb_image_with_a_gray_profile():
    gray = Image.open("tests/fixtures/images/grayscale-icc.jpg")
    icc = gray.info["icc_profile"]
    expected = convert_to_srgb(gray, icc)

    converted = convert_to_srgb(gray.convert("RGB"), icc)

    assert converted.mode == "RGB"
    assert converted.convert("L").tobytes() == expected.tobytes()

    with_alpha = gray.convert("RGBA")
    with_alpha.putalpha(Image.linear_gradient("L").resize(gray.size))

    converted = convert_to_srgb(with_alpha, icc)

    assert converted.mode == "RGBA"
    assert converted.getchannel("A").tobytes() == (
        with_alpha.getchannel("A").tobytes()
    )
    assert converted.convert("RGB").convert("L").tobytes() == (
        expected.tobytes()
    )


@pytest.mark.parametrize("tag", [b"rXYZ", b"rTRC"])
def test_convert_to_srgb_refuses_a_profile_it_cannot_use(tag):
    img = Image.new("RGB", (8, 8))

    assert convert_to_srgb(img, srgb_icc().replace(tag, b"none", 1)) is None


def test_renders_as_srgb():
    _, linear_p3 = linear_p3_image()
    gray = Image.open("tests/fixtures/images/grayscale-icc.jpg")
    cmyk = Image.open("tests/fixtures/images/cmyk-icc.jpg")

    assert renders_as_srgb(srgb_icc())
    assert not renders_as_srgb(linear_p3)
    assert not renders_as_srgb(gray.info["icc_profile"])
    assert not renders_as_srgb(cmyk.info["icc_profile"])
    assert not renders_as_srgb(srgb_icc().replace(b"rXYZ", b"none", 1))
    assert not renders_as_srgb(b"invalid")
    assert not renders_as_srgb(None)

    with mock.patch("thumbor.utils.ImageCms", new=None):
        assert not renders_as_srgb(srgb_icc())


@pytest.mark.parametrize("mode", ["P", "CMYK", "I;16"])
def test_convert_to_srgb_refuses_a_mode_the_profile_does_not_describe(mode):
    img, icc = linear_p3_image(mode)

    assert convert_to_srgb(img, icc) is None


def test_convert_to_srgb_refuses_an_invalid_profile():
    img = Image.new("RGB", (8, 8))

    assert convert_to_srgb(img, b"invalid") is None


def test_convert_to_srgb_needs_imagecms():
    img, icc = linear_p3_image()

    with mock.patch("thumbor.utils.ImageCms", new=None):
        assert convert_to_srgb(img, icc) is None
