#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from __future__ import unicode_literals, absolute_import
from os.path import abspath, join, dirname
import warnings

from unittest import TestCase, skipUnless
from preggy import expect

from thumbor.context import Context
from thumbor.config import Config
from thumbor.engines.pil import Engine

try:
    from pyexiv2 import ImageMetadata
    METADATA_AVAILABLE = True
except ImportError:
    METADATA_AVAILABLE = False

STORAGE_PATH = abspath(join(dirname(__file__), '../fixtures/images/'))

class PilEngineTestCase(TestCase):

    def get_context(self):
        cfg = Config(
                SECURITY_KEY='ACME-SEC',
                ENGINE = 'thumbor.engines.pil',
                IMAGE_METADATA_READ_FORMATS = 'exif,xmp'
        )
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = STORAGE_PATH
        cfg.STORAGE = 'thumbor.storages.no_storage'

        return Context(config=cfg)

    def setUp(self):
        self.context = self.get_context()

    def test_create_engine(self):
        engine = Engine(self.context)
        expect(engine).to_be_instance_of(Engine)

    def test_load_image(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, 'image.jpg'), 'r') as im:
            buffer = im.read()
        image = engine.create_image(buffer)
        expect(image.format).to_equal('JPEG')

    @skipUnless(METADATA_AVAILABLE, 'Pyexiv2 library not found. Skipping metadata tests.')
    def test_load_image_with_metadata(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, 'BlueSquare.jpg'), 'r') as im:
            buffer = im.read()

        engine.load(buffer, None)
        image = engine.image
        expect(image.format).to_equal('JPEG')
        expect(engine.metadata).Not.to_be_null()
        expect(engine.metadata.__class__.__name__).to_equal('ImageMetadata')

        # read the xmp tags
        xmp_keys = engine.metadata.xmp_keys
        expect(len(xmp_keys)).to_equal(27)
        expect('Xmp.tiff.ImageWidth' in xmp_keys).to_be_true()

        width = engine.metadata[b'Xmp.tiff.ImageWidth'].value
        expect(width).to_equal(360)

        # read EXIF tags
        exif_keys = engine.metadata.exif_keys
        expect(len(exif_keys)).to_equal(17)
        expect('Exif.Image.Orientation' in exif_keys).to_be_true()
        expect(engine.metadata[b'Exif.Image.Orientation'].value).to_equal(1)

        # read IPTC tags
        iptc_keys = engine.metadata.iptc_keys
        expect(len(iptc_keys)).to_equal(4)
        expect('Iptc.Application2.Keywords' in iptc_keys).to_be_true()
        expect(engine.metadata[b'Iptc.Application2.Keywords'].value).to_equal(
            ['XMP', 'Blue Square', 'test file', 'Photoshop', '.jpg']
        )
