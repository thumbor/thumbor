# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import tempfile
from os.path import abspath, dirname, join

import pytest
from tornado.testing import gen_test

from tests.base import TestCase
from tests.fixtures.transformer_test_data import (
    FIT_IN_CROP_DATA,
    TESTITEMS,
    MockErrorSyncDetector,
    MockSyncDetector,
    TestData,
)
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.importer import Importer
from thumbor.transformer import Transformer


class TransformerTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root_folder = (
            tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        )
        cls.root_path = cls.root_folder.name
        cls.loader_path = abspath(
            join(dirname(__file__), "../fixtures/images/")
        )
        cls.base_uri = "/image"

    @classmethod
    def tearDownClass(cls):
        if cls.root_folder is not None:
            cls.root_folder.cleanup()

    def setUp(self):
        super().setUp()
        self.has_handled = False

    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.file_storage"
        cfg.FILE_STORAGE_ROOT_PATH = self.root_path

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    @gen_test
    async def test_invalid_crop(self):
        data = TestData(
            source_width=800,
            source_height=600,
            target_width=800,
            target_height=600,
            halign="right",
            valign="top",
            focal_points=[],
            crop_left=200,
            crop_top=0,
            crop_right=100,
            crop_bottom=100,
        )

        ctx = data.to_context()
        engine = ctx.modules.engine

        trans = Transformer(ctx)

        await trans.transform()
        assert not engine.calls["crop"]

    @staticmethod
    def validate_resize(test_data):
        assert test_data.has_resized_properly()
        assert test_data.has_cropped_properly()

    @gen_test
    async def test_can_resize_images(self):
        for item in TESTITEMS:
            context = item.to_context()
            trans = Transformer(context)
            await trans.transform()
            self.validate_resize(item)

    @gen_test
    async def test_can_resize_images_with_detectors(self):
        for item in TESTITEMS:
            context = item.to_context(detectors=[MockSyncDetector])
            trans = Transformer(context)
            await trans.transform()
            self.validate_resize(item)

    @gen_test
    async def test_can_resize_images_with_detection_error(self):
        test_data = TestData(
            source_width=800,
            source_height=600,
            target_width=400,
            target_height=150,
            halign="center",
            valign="middle",
            focal_points=[],
            crop_left=0,
            crop_top=75,
            crop_right=800,
            crop_bottom=375,
        )
        context = test_data.to_context(
            detectors=[MockErrorSyncDetector], ignore_detector_error=True
        )
        trans = Transformer(context)
        await trans.transform()
        self.validate_resize(test_data)

    @gen_test
    async def test_can_resize_images_with_detection_error_not_ignoring_it(
        self,
    ):
        test_data = TestData(
            source_width=800,
            source_height=600,
            target_width=400,
            target_height=150,
            halign="center",
            valign="middle",
            focal_points=[],
            crop_left=0,
            crop_top=75,
            crop_right=800,
            crop_bottom=375,
        )
        context = test_data.to_context(
            detectors=[MockErrorSyncDetector], ignore_detector_error=False
        )
        trans = Transformer(context)

        with pytest.raises(IOError, match="some-io-error"):
            await trans.transform()

        assert len(test_data.engine.calls["resize"]) == 0

    @gen_test
    async def test_can_fit_in(self):
        for test_data, (width, height, should_resize) in FIT_IN_CROP_DATA:
            context = test_data.to_context()
            engine = context.modules.engine
            trans = Transformer(context)

            await trans.transform()

            assert not engine.calls["crop"]
            if should_resize:
                assert len(engine.calls["resize"]) == 1
                assert engine.calls["resize"][0]["width"] == width
                assert engine.calls["resize"][0]["height"] == height
            else:
                assert not engine.calls["resize"]

    @gen_test
    async def test_can_transform_meta_with_orientation(self):
        data = TestData(
            source_width=800,
            source_height=600,
            target_width=100,
            target_height=100,
            halign="right",
            valign="top",
            focal_points=[],
            crop_left=None,
            crop_top=None,
            crop_right=None,
            crop_bottom=None,
            meta=True,
        )

        ctx = data.to_context()
        ctx.config.RESPECT_ORIENTATION = True
        engine = ctx.modules.engine

        trans = Transformer(ctx)
        await trans.transform()
        assert engine.calls["reorientate"] == 1

    @gen_test
    async def test_can_transform_with_flip(self):
        data = TestData(
            source_width=800,
            source_height=600,
            target_width=-800,
            target_height=-600,
            halign="right",
            valign="top",
            focal_points=[],
            crop_left=None,
            crop_top=None,
            crop_right=None,
            crop_bottom=None,
        )
        ctx = data.to_context()
        engine = ctx.modules.engine
        trans = Transformer(ctx)

        await trans.transform()

        assert engine.calls["horizontal_flip"] == 1
        assert engine.calls["vertical_flip"] == 1

    @gen_test
    async def test_can_resize_with_stretch(self):
        data = TestData(
            source_width=800,
            source_height=600,
            target_width=800,
            target_height=200,
            halign="right",
            valign="top",
            focal_points=[],
            crop_left=None,
            crop_top=None,
            crop_right=None,
            crop_bottom=None,
            stretch=True,
        )
        ctx = data.to_context()
        engine = ctx.modules.engine
        trans = Transformer(ctx)

        await trans.transform()

        assert engine.calls["resize"] == [{"width": 800, "height": 200}]
        assert not engine.calls["crop"]

    @gen_test
    async def test_can_extract_cover(self):
        data = TestData(
            source_width=800,
            source_height=600,
            target_width=-800,
            target_height=-600,
            halign="right",
            valign="top",
            focal_points=[],
            crop_left=None,
            crop_top=None,
            crop_right=None,
            crop_bottom=None,
        )
        ctx = data.to_context()
        ctx.request.filters = "cover()"
        ctx.request.image = "some.gif"
        ctx.request.extension = "GIF"
        ctx.request.engine.extension = ".gif"
        ctx.config.USE_GIFSICLE_ENGINE = True
        engine = ctx.modules.engine
        trans = Transformer(ctx)

        await trans.transform()

        assert engine.calls["cover"] == 1

    @gen_test
    async def test_get_target_dimensions(self):
        data = TestData(
            source_width=800,
            source_height=600,
            target_width=600,
            target_height=400,
            halign="right",
            valign="top",
            focal_points=[],
            crop_left=200,
            crop_top=0,
            crop_right=100,
            crop_bottom=100,
        )

        ctx = data.to_context()
        trans = Transformer(ctx)
        dimensions = trans.get_target_dimensions()
        assert dimensions == (600, 400)

        await trans.transform()

        assert dimensions == (600, 400)
