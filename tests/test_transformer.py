#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import tempfile
import shutil
from os.path import abspath, join, dirname

from preggy import expect

from thumbor.transformer import Transformer
from thumbor.config import Config
from thumbor.importer import Importer
from thumbor.context import Context, ServerParameters
from tests.base import TestCase
from tests.fixtures.transformer_test_data import (
    TESTITEMS, MockSyncDetector, FIT_IN_CROP_DATA, TestData,
    MockErrorSyncDetector,
)


class TransformerTestCase(TestCase):
    @classmethod
    def setUpClass(cls, *args, **kw):
        cls.root_path = tempfile.mkdtemp()
        cls.loader_path = abspath(join(dirname(__file__), '../fixtures/images/'))
        cls.base_uri = "/image"

    @classmethod
    def tearDownClass(cls, *args, **kw):
        shutil.rmtree(cls.root_path)

    def setUp(self):
        super(TransformerTestCase, self).setUp()
        self.has_handled = False

    def get_context(self):
        cfg = Config(SECURITY_KEY='ACME-SEC')
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.file_storage"
        cfg.FILE_STORAGE_ROOT_PATH = self.root_path

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        return Context(server, cfg, importer)

    def test_invalid_crop(self):
        data = TestData(
            source_width=800, source_height=600,
            target_width=800, target_height=600,
            halign="right", valign="top",
            focal_points=[],
            crop_left=200, crop_top=0, crop_right=100, crop_bottom=100
        )

        ctx = data.to_context()
        engine = ctx.modules.engine

        trans = Transformer(ctx)
        trans.transform(lambda: None)
        expect(engine.calls['crop']).to_be_empty()

    def validate_resize(self, test_data):
        expect(test_data).to_be_resized()
        expect(test_data).to_be_cropped()

    def test_can_resize_images(self):
        for item in TESTITEMS:
            context = item.to_context()
            trans = Transformer(context)
            trans.transform(lambda: None)
            self.validate_resize(item)

    def test_can_resize_images_with_detectors(self):
        for item in TESTITEMS:
            context = item.to_context(detectors=[MockSyncDetector])
            trans = Transformer(context)
            trans.transform(lambda: None)
            self.validate_resize(item)

    def test_can_resize_images_with_detection_error(self):
        test_data = TestData(
            source_width=800, source_height=600,
            target_width=400, target_height=150,
            halign="center", valign="middle",
            focal_points=[],
            crop_left=0, crop_top=75, crop_right=800, crop_bottom=375
        )
        context = test_data.to_context(detectors=[MockErrorSyncDetector], ignore_detector_error=True)
        trans = Transformer(context)
        trans.transform(lambda: None)
        self.validate_resize(test_data)

    def test_can_resize_images_with_detection_error_not_ignoring_it(self):
        test_data = TestData(
            source_width=800, source_height=600,
            target_width=400, target_height=150,
            halign="center", valign="middle",
            focal_points=[],
            crop_left=0, crop_top=75, crop_right=800, crop_bottom=375
        )
        context = test_data.to_context(detectors=[MockErrorSyncDetector], ignore_detector_error=False)
        trans = Transformer(context)

        trans.transform(lambda: None)

        expect(test_data.engine.calls['resize']).to_length(0)

    def test_can_fit_in(self):
        for (test_data, (width, height, should_resize)) in FIT_IN_CROP_DATA:
            context = test_data.to_context()
            engine = context.modules.engine

            trans = Transformer(context)
            trans.transform(lambda: None)

            expect(engine.calls['crop']).to_be_empty()

            if should_resize:
                expect(engine.calls['resize']).to_length(1)
                expect(engine.calls['resize'][0]['width']).to_equal(width)
                expect(engine.calls['resize'][0]['height']).to_equal(height)
            else:
                expect(engine.calls['resize']).to_be_empty()

    def test_can_transform_meta_with_orientation(self):
        data = TestData(
            source_width=800, source_height=600,
            target_width=100, target_height=100,
            halign="right", valign="top",
            focal_points=[],
            crop_left=None, crop_top=None, crop_right=None, crop_bottom=None,
            meta=True
        )

        ctx = data.to_context()
        ctx.config.RESPECT_ORIENTATION = True
        engine = ctx.modules.engine

        trans = Transformer(ctx)
        trans.transform(lambda: None)
        expect(engine.calls['reorientate']).to_equal(1)

    def test_can_transform_with_flip(self):
        data = TestData(
            source_width=800, source_height=600,
            target_width=-800, target_height=-600,
            halign="right", valign="top",
            focal_points=[],
            crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
        )

        ctx = data.to_context()
        engine = ctx.modules.engine

        trans = Transformer(ctx)
        trans.transform(lambda: None)
        expect(engine.calls['horizontal_flip']).to_equal(1)
        expect(engine.calls['vertical_flip']).to_equal(1)

    def test_can_extract_cover(self):
        data = TestData(
            source_width=800, source_height=600,
            target_width=-800, target_height=-600,
            halign="right", valign="top",
            focal_points=[],
            crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
        )

        ctx = data.to_context()
        ctx.request.filters = 'cover()'
        ctx.request.image = 'some.gif'
        ctx.request.extension = 'GIF'
        ctx.request.engine.extension = '.gif'
        ctx.config.USE_GIFSICLE_ENGINE = True

        engine = ctx.modules.engine

        trans = Transformer(ctx)
        trans.transform(lambda: None)
        expect(engine.calls['cover']).to_equal(1)

    def test_get_target_dimensions(self):
        data = TestData(
            source_width=800, source_height=600,
            target_width=600, target_height=400,
            halign="right", valign="top",
            focal_points=[],
            crop_left=200, crop_top=0, crop_right=100, crop_bottom=100
        )

        ctx = data.to_context()
        trans = Transformer(ctx)
        dimensions = trans.get_target_dimensions()
        expect(dimensions).to_equal((600, 400))
        trans.transform(lambda: 1)
        expect(dimensions).to_equal((600, 400))
