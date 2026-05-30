# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from tornado.testing import gen_test

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
