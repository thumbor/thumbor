#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from __future__ import unicode_literals, absolute_import
from os.path import abspath, join, dirname

from unittest import TestCase, skipUnless
from preggy import expect

from PIL import Image

from thumbor.context import Context
from thumbor.config import Config
from thumbor.engines.pil import Engine

try:
    from pyexiv2 import ImageMetadata  # noqa
    METADATA_AVAILABLE = True
except ImportError:
    METADATA_AVAILABLE = False

import datetime
import mock

STORAGE_PATH = abspath(join(dirname(__file__), '../fixtures/images/'))


class PilEngineTestCase(TestCase):

    def get_context(self):
        cfg = Config(
            SECURITY_KEY='ACME-SEC',
            ENGINE='thumbor.engines.pil',
            IMAGE_METADATA_READ_FORMATS='exif,xmp'
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

    def test_convert_tif_16bit_per_channel_lsb_to_png(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, 'gradient_lsb_16bperchannel.tif'), 'r') as im:
            buffer = im.read()
        expect(buffer).not_to_equal(None)
        engine.convert_tif_to_png(buffer)
        expect(engine.extension).to_equal('.png')

    def test_convert_tif_16bit_per_channel_msb_to_png(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, 'gradient_msb_16bperchannel.tif'), 'r') as im:
            buffer = im.read()
        engine.convert_tif_to_png(buffer)
        expect(engine.extension).to_equal('.png')

    def test_convert_tif_8bit_per_channel_to_png(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, 'gradient_8bit.tif'), 'r') as im:
            buffer = im.read()
        engine.convert_tif_to_png(buffer)
        expect(engine.extension).to_equal('.png')

    def test_convert_png_1bit_to_png(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, '1bit.png'), 'r') as im:
            buffer = im.read()
        engine.load(buffer, '.png')
        engine.resize(10, 10)
        mode, _ = engine.image_data_as_rgb()
        expect(mode).to_equal('P')  # Note that this is not a true 1bit image, it's 8bit in black/white.

    def test_convert_should_preserve_palette_mode(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, '256_color_palette.png'), 'r') as im:
            buffer = im.read()
        engine.load(buffer, '.png')
        engine.resize(10, 10)
        mode, _ = engine.image_data_as_rgb()
        expect(mode).to_equal('P')

    def test_can_set_resampling_filter(self):
        to_test = {
            'LANCZOS': Image.LANCZOS,
            'NEAREST': Image.NEAREST,
            'BiLinear': Image.BILINEAR,
            'bicubic': Image.BICUBIC,
            'garbage': Image.LANCZOS,
        }

        if hasattr(Image, 'HAMMING'):
            to_test['HAMMING'] = Image.HAMMING

        for setting, expected in to_test.items():
            cfg = Config(PILLOW_RESAMPLING_FILTER=setting)
            engine = Engine(Context(config=cfg))
            expect(engine.get_resize_filter()).to_equal(expected)

        cfg = Config()
        engine = Engine(Context(config=cfg))
        expect(engine.get_resize_filter()).to_equal(Image.LANCZOS)

    @mock.patch('thumbor.engines.pil.cv2', new=None)
    @mock.patch('thumbor.engines.logger.error')
    def test_not_imported_cv2_failed_to_convert_tif_to_png(self, mockLogError):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, 'gradient_8bit.tif'), 'r') as im:
            buffer = im.read()
        returned_buffer = engine.convert_tif_to_png(buffer)
        expect(mockLogError.called).to_be_true()
        expect(buffer).to_equal(returned_buffer)

    def test_resize_truncated_image(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, 'BlueSquare_truncated.jpg'), 'r') as im:
            buffer = im.read()
        engine.load(buffer, '.jpg')
        engine.resize(10, 10)
        mode, _ = engine.image_data_as_rgb()
        expect(mode).to_equal('RGB')

    @skipUnless(METADATA_AVAILABLE, 'Pyexiv2 library not found. Skipping metadata tests.')
    def test_load_image_with_metadata(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, 'Christophe_Henner_-_June_2016.jpg'), 'r') as im:
            buffer = im.read()

        engine.load(buffer, None)
        image = engine.image
        expect(image.format).to_equal('JPEG')
        expect(engine.metadata).Not.to_be_null()
        expect(engine.metadata.__class__.__name__).to_equal('ImageMetadata')

        # read the xmp tags
        xmp_keys = engine.metadata.xmp_keys
        expect(len(xmp_keys)).to_equal(44)
        expect('Xmp.aux.LensSerialNumber' in xmp_keys).to_be_true()

        width = engine.metadata[b'Xmp.aux.LensSerialNumber'].value
        expect(width).to_equal('0000c139be')

        # read EXIF tags
        exif_keys = engine.metadata.exif_keys
        expect(len(exif_keys)).to_equal(37)
        expect('Exif.Image.Software' in exif_keys).to_be_true()
        expect(engine.metadata[b'Exif.Image.Software'].value).to_equal('Adobe Photoshop Lightroom 4.4 (Macintosh)')

        # read IPTC tags
        iptc_keys = engine.metadata.iptc_keys
        expect(len(iptc_keys)).to_equal(6)
        expect('Iptc.Application2.DateCreated' in iptc_keys).to_be_true()
        expect(engine.metadata[b'Iptc.Application2.DateCreated'].value).to_equal(
            [datetime.date(2016, 6, 23)]
        )
