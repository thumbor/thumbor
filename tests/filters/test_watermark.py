# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from tornado.testing import gen_test

from tests.fixtures.watermark_fixtures import (
    POSITIONS,
    RATIOS,
    SOURCE_IMAGE_SIZES,
    WATERMARK_IMAGE_SIZES,
    assert_almost_equal,
    assert_equal_with_info,
    assert_fits_into,
    assert_true_with_info,
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
        assert ssim > 0.98

    @gen_test
    async def test_watermark_filter_centered_x(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,center,40,20)",
        )
        expected = self.get_fixture("watermarkCenterX.jpg")
        ssim = self.get_ssim(image, expected)
        assert ssim > 0.98

    @gen_test
    async def test_watermark_filter_centered_y(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,80,center,50)",
        )
        expected = self.get_fixture("watermarkCenterY.jpg")
        ssim = self.get_ssim(image, expected)
        assert ssim > 0.98

    @gen_test
    async def test_watermark_filter_repeated(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,repeat,repeat,70)",
        )
        expected = self.get_fixture("watermarkRepeat.jpg")
        ssim = self.get_ssim(image, expected)
        assert ssim > 0.98

    @gen_test
    async def test_watermark_filter_repeated_x(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,repeat,center,70)",
        )
        expected = self.get_fixture("watermarkRepeatX.jpg")
        ssim = self.get_ssim(image, expected)
        assert ssim > 0.98

    @gen_test
    async def test_watermark_filter_repeated_y(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,30,repeat,30)",
        )
        expected = self.get_fixture("watermarkRepeatY.jpg")
        ssim = self.get_ssim(image, expected)
        assert ssim > 0.98

    @gen_test
    async def test_watermark_filter_detect_extension_simple(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark,30,-50,60)",
        )
        expected = self.get_fixture("watermarkSimple.jpg")
        ssim = self.get_ssim(image, expected)
        assert ssim > 0.98

    @gen_test
    async def test_watermark_filter_simple(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,30,-50,60)",
        )
        expected = self.get_fixture("watermarkSimple.jpg")
        ssim = self.get_ssim(image, expected)
        assert ssim > 0.98

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
        assert ssim > 0.98

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
        assert ssim > 0.98

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
        assert ssim > 0.98

    @gen_test
    async def test_watermark_filter_calculated_position(self):
        watermark.Filter.pre_compile()
        filter_instance = watermark.Filter(
            "http://dummy,0,0,0", self.context  # NOSONAR
        )

        for length, pos, expected in POSITIONS:
            test = {
                "length": length,
                "pos": pos,
            }

            assert_equal_with_info(
                filter_instance.detect_and_get_ratio_position(pos, length),
                expected,
                **test,
            )

    @gen_test
    async def test_watermark_filter_simple_big(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermarkBig.png,-10,-100,50)",
        )
        expected = self.get_fixture("watermarkSimpleBig.jpg")
        ssim = self.get_ssim(image, expected)
        assert ssim > 0.98

    @gen_test
    async def test_watermark_filter_simple_50p_width(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,30,-50,20,50)",
        )
        expected = self.get_fixture("watermarkResize50pWidth.jpg")
        ssim = self.get_ssim(image, expected)
        assert ssim > 0.98

    @gen_test
    async def test_watermark_filter_simple_70p_height(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,30,-50,20,none,70)",
        )
        expected = self.get_fixture("watermarkResize70pHeight.jpg")
        ssim = self.get_ssim(image, expected)
        assert ssim > 0.98

    @gen_test
    async def test_watermark_filter_simple_60p_80p(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,-30,-200,20,60,80)",
        )
        expected = self.get_fixture("watermarkResize60p80p.jpg")
        ssim = self.get_ssim(image, expected)
        assert ssim > 0.98

    @gen_test
    async def test_watermark_filter_float_w_ratio_matches_integer(self):
        image_float = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,30,-50,20,50.0)",
        )
        image_int = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,30,-50,20,50)",
        )
        ssim = self.get_ssim(image_float, image_int)
        assert ssim == 1

    @gen_test
    async def test_watermark_filter_float_h_ratio_matches_integer(self):
        image_float = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,30,-50,20,none,70.0)",
        )
        image_int = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,30,-50,20,none,70)",
        )
        ssim = self.get_ssim(image_float, image_int)
        assert ssim == 1

    @gen_test
    async def test_watermark_filter_float_w_and_h_ratio_matches_integer(self):
        image_float = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,-30,-200,20,60.0,80.0)",
        )
        image_int = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.watermark",
            "watermark(watermark.png,-30,-200,20,60,80)",
        )
        ssim = self.get_ssim(image_float, image_int)
        assert ssim == 1

    async def get_watermark_size(self, params_string):
        fltr = self.get_filter("thumbor.filters.watermark", params_string)
        with open(self.get_fixture_path("source.jpg"), "rb") as source:
            fltr.engine.load(source.read(), ".jpg")
        await fltr.run()
        return fltr.watermark_engine.size

    @gen_test
    async def test_watermark_filter_fractional_w_ratio_size(self):
        size = await self.get_watermark_size(
            "watermark(watermark.png,30,-50,20,9.5)"
        )
        assert size == (76, 76)

    @gen_test
    async def test_watermark_filter_fractional_h_ratio_size(self):
        size = await self.get_watermark_size(
            "watermark(watermark.png,30,-50,20,none,12.5)"
        )
        assert size == (67, 67)

    @gen_test
    async def test_watermark_filter_fractional_w_and_h_ratio_size(self):
        size = await self.get_watermark_size(
            "watermark(watermark.png,30,-50,20,12.7,75.25)"
        )
        assert size == (102, 102)

    @gen_test
    async def test_watermark_filter_tiny_ratio_keeps_one_pixel(self):
        size = await self.get_watermark_size(
            "watermark(watermark.png,30,-50,20,0.01)"
        )
        assert size == (1, 1)

    def test_watermark_filter_rejects_negative_ratios(self):
        watermark.Filter.pre_compile()
        for ratios in ("-9.5", "none,-9.5", "-50"):
            fltr = watermark.Filter(
                f"watermark(watermark.png,30,-50,20,{ratios})"
            )
            assert fltr.params is None, ratios

    def test_watermark_calc_size_fractional_ratio(self):
        size = watermark.Filter.calc_watermark_size(
            (600, 400), (30, 30), 0.095, False
        )
        assert size == (57, 57)

    def test_watermark_calc_size_keeps_each_side_at_least_one_pixel(self):
        size = watermark.Filter.calc_watermark_size(
            (800, 600), (1200, 500), 0.001, False
        )
        assert size == (1, 1)

    @gen_test
    async def test_watermark_filter_calculated_resizing(self):
        watermark.Filter.pre_compile()
        filter_instance = watermark.Filter(
            "http://dummy,0,0,0", self.context  # NOSONAR
        )

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

                    # Sizes are rounded to whole pixels.
                    test["topic_name"] = "watermark_image_width"
                    assert_fits_into(
                        watermark_image_width, max_width + 0.5, **test
                    )
                    test["topic_name"] = "watermark_image_height"
                    assert_fits_into(
                        watermark_image_height, max_height + 0.5, **test
                    )

                    test["topic_name"] = "fill out"
                    assert_true_with_info(
                        (
                            abs(watermark_image_width - max_width) <= 0.5
                            or abs(watermark_image_height - max_height) <= 0.5
                        ),
                        **test,
                    )

                    test["topic_name"] = "image ratio"
                    assert_almost_equal(watermark_image, ratio, 2, **test)

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

        assert not filter_instance.validate("https://s2.glbimg.com/logo.jpg")
        assert filter_instance.validate("https://s.glbimg.com/logo.jpg")
