# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from io import BytesIO

import pytest
from PIL import Image, ImageChops
from tornado.testing import gen_test

from tests.base import FilterTestCase


async def round_transparent_image(source, radius, extension=".png"):
    fltr = FilterTestCase().get_filter(
        "thumbor.filters.round_corner", f"round_corner({radius},0,0,0,1)"
    )
    with BytesIO() as buffer:
        source.save(buffer, "PNG")
        fltr.engine.load(buffer.getvalue(), ".png")
    await fltr.run()
    with Image.open(
        BytesIO(fltr.engine.read(extension, quality=100))
    ) as result:
        return result.convert("RGBA")


@pytest.mark.asyncio
@pytest.mark.parametrize("radius", ["30", "20|35", "150"])
@pytest.mark.parametrize("mode, alpha", [("RGB", 255), ("RGBA", 128)])
@pytest.mark.parametrize("extension", [".png", ".webp"])
async def test_transparent_round_corners_have_no_dark_border(
    radius, mode, alpha, extension
):
    source = Image.new(mode, (100, 100), "white")
    if mode == "RGBA":
        source.putalpha(alpha)
    result = await round_transparent_image(source, radius, extension)

    background = Image.new("RGBA", source.size, "white")
    composite = Image.alpha_composite(background, result).convert("RGB")
    assert composite.getextrema() == ((255, 255),) * 3
    assert result.getpixel((50, 50)) == (255, 255, 255, alpha)

    for box in (
        (0, 0, 50, 50),
        (50, 0, 100, 50),
        (0, 50, 50, 100),
        (50, 50, 100, 100),
    ):
        histogram = result.getchannel("A").crop(box).histogram()
        assert histogram[0] > 0
        assert histogram[alpha] > 0
        assert sum(histogram[1:alpha]) > 0
        assert sum(histogram[alpha + 1 :]) == 0


@pytest.mark.asyncio
async def test_transparent_round_corners_preserve_existing_color_and_alpha():
    source = Image.new("RGBA", (100, 100))
    source.putdata(
        [
            (2 * x, 2 * y, 150, ((x + y) % 3) * 127)
            for y in range(100)
            for x in range(100)
        ]
    )
    result = await round_transparent_image(source, "20|35")

    assert (
        ImageChops.difference(
            result.convert("RGB"), source.convert("RGB")
        ).getbbox()
        is None
    )
    assert (
        ImageChops.subtract(
            result.getchannel("A"), source.getchannel("A")
        ).getbbox()
        is None
    )
    assert result.getpixel((50, 50)) == source.getpixel((50, 50))


class RoundCornerFilterTestCase(FilterTestCase):
    @gen_test
    async def test_round_corner_filter_with_a_radius(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.round_corner",
            "round_corner(50,255,0,0)",
        )
        expected = self.get_fixture("round_corner.jpg")

        ssim = self.get_ssim(image, expected)
        assert ssim > 0.99

    @gen_test
    async def test_round_corner_filter_with_ab_radius(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.round_corner",
            "round_corner(50|75,255,0,0)",
        )
        expected = self.get_fixture("round_corner1.jpg")

        ssim = self.get_ssim(image, expected)
        assert ssim > 0.99

    @gen_test
    async def test_round_corner_filter_with_blue_background(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.round_corner",
            "round_corner(50,0,0,255)",
        )
        expected = self.get_fixture("round_corner2.jpg")

        ssim = self.get_ssim(image, expected)
        assert ssim > 0.99

    @gen_test
    async def test_round_corner_filter_without_transparent(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.round_corner",
            "round_corner(50,255,0,0,0)",
        )
        expected = self.get_fixture("round_corner3.jpg")

        ssim = self.get_ssim(image, expected)
        assert ssim > 0.99

    @gen_test
    async def test_round_corner_filter_with_transparent(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.round_corner",
            "round_corner(50,255,0,0,1)",
        )
        expected = self.get_fixture("round_corner3.jpg")

        ssim = self.get_ssim(image, expected)
        assert ssim > 0.99

    @gen_test
    async def test_round_corner_filter_with_transparent_by_png(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.round_corner",
            "round_corner(50,255,0,0,1)",
            mode="RGBA",
        )
        expected = self.get_fixture("round_corner.png", mode="RGBA")

        ssim = self.get_ssim(image, expected)
        assert ssim > 0.99

    @gen_test
    async def test_round_corner_filter_with_transparent_by_webp(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.round_corner",
            "round_corner(50,255,0,0,1)",
            mode="RGBA",
        )
        expected = self.get_fixture("round_corner.webp", mode="RGBA")

        ssim = self.get_ssim(image, expected)
        assert ssim > 0.99
