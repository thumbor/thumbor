# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import pytest
from tornado.testing import gen_test
from tornado.web import HTTPError

from tests.base import FilterTestCase
from thumbor.filters.format import get_allowed_conversions, normalize_format


def allowed_conversions(conversions, extension=".jpg"):
    def config_context(context):
        context.config.FORMAT_FILTER_ALLOWED_CONVERSIONS = conversions
        if extension is not None:
            context.request.extension = extension

    return config_context


class FormatFilterTestCase(FilterTestCase):
    @gen_test
    async def test_invalid_format_should_be_null(self):
        await self.get_filtered(
            "source.jpg", "thumbor.filters.format", "format(invalid)"
        )
        assert self.context.request.format is None

    @gen_test
    async def test_can_set_proper_format(self):
        await self.get_filtered(
            "source.jpg", "thumbor.filters.format", "format(webp)"
        )
        assert self.context.request.format == "webp"

    async def assert_conversion_rejected(self, params, config_context):
        with self.assertRaises(HTTPError) as error:
            await self.get_filtered(
                "source.jpg", "thumbor.filters.format", params, config_context
            )

        assert error.exception.status_code == 400
        assert self.context.request.format is None

    @gen_test
    async def test_should_allow_listed_conversion(self):
        await self.get_filtered(
            "source.jpg",
            "thumbor.filters.format",
            "format(webp)",
            allowed_conversions({"jpg": ["webp"]}),
        )
        assert self.context.request.format == "webp"

    @gen_test
    async def test_should_reject_conversion_not_listed(self):
        await self.assert_conversion_rejected(
            "format(png)", allowed_conversions({"jpg": ["webp"]})
        )

    @gen_test
    async def test_should_reject_source_format_not_listed(self):
        await self.assert_conversion_rejected(
            "format(jpg)", allowed_conversions({"jpg": ["webp"]})
        )

    @gen_test
    async def test_should_reject_invalid_format_for_listed_source(self):
        await self.assert_conversion_rejected(
            "format(invalid)", allowed_conversions({"jpg": ["webp"]})
        )

    @gen_test
    async def test_should_reject_invalid_format_matching_an_allowed_one(self):
        await self.assert_conversion_rejected(
            "format(.png)", allowed_conversions({"jpg": ["png"]})
        )

    @gen_test
    async def test_should_reject_every_format_for_empty_list(self):
        await self.assert_conversion_rejected(
            "format(jpg)", allowed_conversions({"jpg": []})
        )

    @gen_test
    async def test_should_not_restrict_sources_not_listed(self):
        await self.get_filtered(
            "source.jpg",
            "thumbor.filters.format",
            "format(webp)",
            allowed_conversions({"png": ["png"]}),
        )
        assert self.context.request.format == "webp"

    @gen_test
    async def test_should_not_restrict_unknown_source(self):
        await self.get_filtered(
            "source.jpg",
            "thumbor.filters.format",
            "format(webp)",
            allowed_conversions({"jpg": ["jpg"]}, extension=None),
        )
        assert self.context.request.format == "webp"

    @gen_test
    async def test_should_match_format_aliases(self):
        for conversions, extension, params, expected in (
            ({"jpeg": ["WEBP"]}, ".jpg", "format(webp)", "webp"),
            ({"JPG": ["heif"]}, ".jpg", "format(HEIC)", "heic"),
            ({"tiff": ["jpeg"]}, ".tif", "format(jpg)", "jpg"),
            ({"tif": ["png"]}, ".tiff", "format(png)", "png"),
        ):
            with self.subTest(conversions=conversions, params=params):
                await self.get_filtered(
                    "source.jpg",
                    "thumbor.filters.format",
                    params,
                    allowed_conversions(conversions, extension),
                )
                assert self.context.request.format == expected


@pytest.mark.parametrize(
    "image_format,expected",
    [
        ("png", "png"),
        ("JPEG", "jpg"),
        (".jpg", "jpg"),
        ("tiff", "tif"),
        ("HEIF", "heic"),
    ],
)
def test_normalize_format(image_format, expected):
    assert normalize_format(image_format) == expected


@pytest.mark.parametrize(
    "conversions,source_extension,expected",
    [
        ({"svg": ["png"]}, ".svg", {"png"}),
        ({"JPEG": ("WEBP", "jpeg")}, ".jpg", {"webp", "jpg"}),
        ({"svg": []}, ".svg", set()),
        ({"svg": ["png"]}, ".png", None),
        ({"svg": ["png"]}, None, None),
    ],
)
def test_get_allowed_conversions(conversions, source_extension, expected):
    assert get_allowed_conversions(conversions, source_extension) == expected
