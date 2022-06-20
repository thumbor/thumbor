#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect
from tornado.testing import gen_test

from tests.fixtures.watermark_fixtures import (
    POSITIONS,
    RATIOS,
    SOURCE_IMAGE_SIZES,
    WATERMARK_IMAGE_SIZES,
)
from thumbor.config import Config
from thumbor.context import Context
from thumbor.filters import watermark
from thumbor.importer import Importer
from thumbor.testing import FilterTestCase


class WatermarkFilterTestCase(FilterTestCase):
    @gen_test
    async def test_watermark_filter_centered(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,center,center,60)",
        )
        expected = self.get_fixture("watermarkCenter.jpg")
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)

    @gen_test
    async def test_watermark_filter_centered_x(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,center,40,20)",
        )
        expected = self.get_fixture("watermarkCenterX.jpg")
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)

    @gen_test
    async def test_watermark_filter_centered_y(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,80,center,50)",
        )
        expected = self.get_fixture("watermarkCenterY.jpg")
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)

    @gen_test
    async def test_watermark_filter_repeated(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,repeat,repeat,70)",
        )
        expected = self.get_fixture("watermarkRepeat.jpg")
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)

    @gen_test
    async def test_watermark_filter_repeated_x(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,repeat,center,70)",
        )
        expected = self.get_fixture("watermarkRepeatX.jpg")
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)

    @gen_test
    async def test_watermark_filter_repeated_y(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,30,repeat,30)",
        )
        expected = self.get_fixture("watermarkRepeatY.jpg")
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)

    @gen_test
    async def test_watermark_filter_detect_extension_simple(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark,30,-50,60)",
        )
        expected = self.get_fixture("watermarkSimple.jpg")
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)

    @gen_test
    async def test_watermark_filter_simple(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,30,-50,60)",
        )
        expected = self.get_fixture("watermarkSimple.jpg")
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)

    @gen_test
    async def test_watermark_filter_calculated(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,4p,-30p,60)",
        )
        expected = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,32,-160,60)",
        )
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)

    @gen_test
    async def test_watermark_filter_calculated_center(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,4p,center,60)",
        )
        expected = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,32,center,60)",
        )
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)

    @gen_test
    async def test_watermark_filter_calculated_repeat(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,repeat,30p,60)",
        )
        expected = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,repeat,160,60)",
        )
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)

    @gen_test
    async def test_watermark_filter_calculated_position(self):
        watermark.Filter.pre_compile()
        filter_instance = watermark.Filter("http://dummy,0,0,0", self.context)

        for length, pos, expected in POSITIONS:
            test = {
                "length": length,
                "pos": pos,
            }

            expect(
                filter_instance.detect_and_get_ratio_position(pos, length)
            ).to_be_equal_with_additional_info(expected, **test)

    @gen_test
    async def test_watermark_filter_simple_big(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermarkBig.png,-10,-100,50)",
        )
        expected = self.get_fixture("watermarkSimpleBig.jpg")
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)

    @gen_test
    async def test_watermark_filter_simple_50p_width(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,30,-50,20,50)",
        )
        expected = self.get_fixture("watermarkResize50pWidth.jpg")
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)

    @gen_test
    async def test_watermark_filter_simple_70p_height(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,30,-50,20,none,70)",
        )
        expected = self.get_fixture("watermarkResize70pHeight.jpg")
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)

    @gen_test
    async def test_watermark_filter_simple_60p_80p(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,-30,-200,20,60,80)",
        )
        expected = self.get_fixture("watermarkResize60p80p.jpg")
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)

    @gen_test
    async def test_watermark_filter_calculated_resizing(self):
        watermark.Filter.pre_compile()
        filter_instance = watermark.Filter("http://dummy,0,0,0", self.context)

        for source_image_width, source_image_height in SOURCE_IMAGE_SIZES:
            for (
                watermark_source_image_width,
                watermark_source_image_height,
            ) in WATERMARK_IMAGE_SIZES:
                for w_ratio, h_ratio in RATIOS:
                    max_width = (
                        source_image_width * (float(w_ratio) / 100)
                        if w_ratio
                        else float("inf")
                    )
                    max_height = (
                        source_image_height * (float(h_ratio) / 100)
                        if h_ratio
                        else float("inf")
                    )
                    w_ratio = float(w_ratio) / 100.0 if w_ratio else False
                    h_ratio = float(h_ratio) / 100.0 if h_ratio else False

                    ratio = (
                        float(watermark_source_image_width)
                        / watermark_source_image_height
                    )

                    (
                        watermark_image_width,
                        watermark_image_height,
                    ) = filter_instance.calc_watermark_size(
                        (source_image_width, source_image_height),
                        (
                            watermark_source_image_width,
                            watermark_source_image_height,
                        ),
                        w_ratio,
                        h_ratio,
                    )
                    watermark_image = (
                        float(watermark_image_width) / watermark_image_height
                    )

                    test = {
                        "source_image_width": source_image_width,
                        "source_image_height": source_image_height,
                        "watermark_source_image_width": watermark_source_image_width,
                        "watermark_source_image_height": watermark_source_image_height,
                        "watermark_image_width": watermark_image_width,
                        "watermark_image_height": watermark_image_height,
                        "w_ratio": w_ratio,
                        "h_ratio": h_ratio,
                    }

                    test["topic_name"] = "watermark_image_width"
                    expect(watermark_image_width).to_fit_into(
                        max_width, **test
                    )
                    test["topic_name"] = "watermark_image_height"
                    expect(watermark_image_height).to_fit_into(
                        max_height, **test
                    )

                    test["topic_name"] = "fill out"
                    expect(
                        (
                            watermark_image_width == max_width
                            or watermark_image_height == max_height
                        )
                    ).to_be_true_with_additional_info(**test)

                    test["topic_name"] = "image ratio"
                    expect(watermark_image).to_almost_equal(ratio, 2, **test)

    @gen_test
    async def test_watermark_validate_allowed_source(self):
        config = Config(
            ALLOWED_SOURCES=[
                "s.glbimg.com",
            ],
            LOADER="thumbor.loaders.http_loader",
        )
        importer = Importer(config)
        importer.import_modules()

        context = Context(config=config, importer=importer)
        filter_instance = watermark.Filter("", context)

        expect(
            filter_instance.validate("https://s2.glbimg.com/logo.jpg")
        ).to_be_false()
        expect(
            filter_instance.validate("https://s.glbimg.com/logo.jpg")
        ).to_be_true()
