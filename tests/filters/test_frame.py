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

    def test_frame_padding_obeys_max_dimensions(self):
        filter_instance = self.get_filter("thumbor.filters.frame")
        filter_instance.context.config.MAX_WIDTH = 10
        filter_instance.context.config.MAX_HEIGHT = 20
        filter_instance.context.config.MAX_PIXELS = 200
        filter_instance.engine.image = filter_instance.engine.gen_image(
            (10, 10), "#fff"
        )

        with self.assertRaises(HTTPError) as error:
            filter_instance.handle_padding((1, 0, 0, 0))

        assert error.exception.status_code == 400
        assert filter_instance.engine.size == (10, 10)

    def test_frame_padding_obeys_max_pixels(self):
        filter_instance = self.get_filter("thumbor.filters.frame")
        filter_instance.context.config.MAX_WIDTH = 0
        filter_instance.context.config.MAX_HEIGHT = 0
        filter_instance.context.config.MAX_PIXELS = 100
        filter_instance.engine.image = filter_instance.engine.gen_image(
            (10, 10), "#fff"
        )

        with self.assertRaises(HTTPError):
            filter_instance.handle_padding((0, 1, 0, 0))

        assert filter_instance.engine.size == (10, 10)
