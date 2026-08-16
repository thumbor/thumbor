# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from tornado.testing import gen_test
from tornado.web import HTTPError

from thumbor.config import Config
from thumbor.context import Context
from thumbor.ext.filters import _nine_patch
from thumbor.filters import frame
from thumbor.importer import Importer
from thumbor.testing import FilterTestCase


class FrameFilterTestCase(FilterTestCase):
    @gen_test
    async def test_frame_validate_allowed_source(self):
        config = Config(
            ALLOWED_SOURCES=[
                "s.glbimg.com",
            ],
            LOADER="thumbor.loaders.http_loader",
        )
        importer = Importer(config)
        importer.import_modules()

        context = Context(config=config, importer=importer)
        filter_instance = frame.Filter("", context)

        assert not filter_instance.validate("https://s2.glbimg.com/logo.jpg")
        assert filter_instance.validate("https://s.glbimg.com/logo.jpg")

    def get_padding_filter(self, size, **limits):
        filter_instance = self.get_filter("thumbor.filters.frame")
        for name, value in limits.items():
            setattr(filter_instance.context.config, name, value)
        filter_instance.engine.image = filter_instance.engine.gen_image(
            size, "#fff"
        )
        return filter_instance

    def assert_padding_rejected(self, filter_instance, padding):
        size = filter_instance.engine.size

        with self.assertRaises(HTTPError) as error:
            filter_instance.handle_padding(padding)

        assert error.exception.status_code == 400
        assert (
            error.exception.reason
            == "Frame padding exceeds configured image limits"
        )
        assert filter_instance.engine.size == size

    def test_frame_padding_obeys_max_width(self):
        filter_instance = self.get_padding_filter((10, 10), MAX_WIDTH=10)

        self.assert_padding_rejected(filter_instance, (1, 0, 0, 0))

    def test_frame_padding_obeys_max_height(self):
        filter_instance = self.get_padding_filter((10, 10), MAX_HEIGHT=10)

        self.assert_padding_rejected(filter_instance, (0, 0, 0, 1))

    def test_frame_padding_obeys_max_pixels(self):
        filter_instance = self.get_padding_filter((10, 10), MAX_PIXELS=100)

        self.assert_padding_rejected(filter_instance, (0, 1, 0, 0))

    def test_frame_padding_may_reach_the_limits(self):
        filter_instance = self.get_padding_filter(
            (10, 10), MAX_WIDTH=12, MAX_HEIGHT=12, MAX_PIXELS=144
        )

        filter_instance.handle_padding((1, 1, 1, 1))

        assert filter_instance.engine.size == (12, 12)

    def test_frame_padding_ignores_disabled_limits(self):
        for max_pixels in (0, None):
            with self.subTest(max_pixels=max_pixels):
                filter_instance = self.get_padding_filter(
                    (10, 10), MAX_WIDTH=0, MAX_HEIGHT=0, MAX_PIXELS=max_pixels
                )

                filter_instance.handle_padding((1, 1, 1, 1))

                assert filter_instance.engine.size == (12, 12)

    def test_frame_keeps_images_already_past_the_limits(self):
        limits = {"MAX_WIDTH": 10, "MAX_HEIGHT": 10, "MAX_PIXELS": 100}

        filter_instance = self.get_padding_filter((20, 20), **limits)
        filter_instance.handle_padding((0, 0, 0, 0))
        assert filter_instance.engine.size == (20, 20)

        filter_instance = self.get_padding_filter(
            (20, 5), MAX_WIDTH=10, MAX_HEIGHT=10
        )
        filter_instance.handle_padding((0, 1, 0, 1))
        assert filter_instance.engine.size == (20, 7)

        filter_instance = self.get_padding_filter((20, 5), **limits)
        self.assert_padding_rejected(filter_instance, (0, 1, 0, 0))


def build_nine_patch(size, stretchy, content):
    pixels = bytearray()
    for y in range(size):
        for x in range(size):
            if (y == 0 and x in stretchy) or (x == 0 and y in stretchy):
                pixels.extend([0, 0, 0, 255])
            elif x in (0, size - 1) or y in (0, size - 1):
                pixels.extend([0, 0, 0, 0])
            else:
                pixels.extend(content)
    return bytes(pixels)


def test_nine_patch_clips_cells_rounded_past_the_target():
    content = [200, 50, 50, 255]
    nine_patch = build_nine_patch(15, {3, 4, 10, 11}, content)
    target = bytes([255, 255, 255, 255] * 14 * 14)

    result = _nine_patch.apply("RGBA", target, 14, 14, nine_patch, 15, 15)

    assert result[-4:] == bytes(content)


def test_nine_patch_accepts_targets_smaller_than_the_fixed_cells():
    content = [200, 50, 50, 255]
    nine_patch = build_nine_patch(15, {3, 4, 10, 11}, content)
    target = bytes([255, 255, 255, 255] * 2 * 2)

    result = _nine_patch.apply("RGBA", target, 2, 2, nine_patch, 15, 15)

    assert result == bytes(content * 4)
