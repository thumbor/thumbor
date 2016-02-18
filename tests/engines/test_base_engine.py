#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from __future__ import unicode_literals, absolute_import
from struct import pack

from unittest import TestCase

try:
    from unittest import mock  # Python 3.3 +
except ImportError:
    import mock  # Python 2.7

from preggy import expect

from thumbor.context import Context
from thumbor.config import Config
from thumbor.engines import BaseEngine


def exif_str(x):
    return b'Exif\x00\x00II*\x00\x08\x00\x00\x00\x05\x00\x12\x01\x03\x00\x01\x00\x00\x00%s\x00\x00\x1a\x01\x05\x00\x01\x00\x00\x00J\x00\x00\x00\x1b\x01\x05\x00\x01\x00\x00\x00R\x00\x00\x00(\x01\x03\x00\x01\x00\x00\x00\x02\x00\x00\x00\x13\x02\x03\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00H\x00\x00\x00\x01\x00\x00\x00H\x00\x00\x00\x01\x00\x00\x00' % pack('h', x)  # noqa


class BaseEngineTestCase(TestCase):

    def get_context(self):
        cfg = Config(
            SECURITY_KEY='ACME-SEC',
            ENGINE='thumbor.engines',
        )
        cfg.STORAGE = 'thumbor.storages.no_storage'

        return Context(config=cfg)

    def flip_horizontally(self):
        ((a, b), (c, d)) = self.image
        self.image = (
            (b, a),
            (d, c)
        )

    def flip_vertically(self):
        ((a, b), (c, d)) = self.image
        self.image = (
            (c, d),
            (a, b)
        )

    def rotate(self, value):
        ((a, b), (c, d)) = self.image
        if value == 270:
            self.image = (
                (c, a),
                (d, b)
            )
        elif value == 180:
            self.image = (
                (d, c),
                (b, a)
            )
        elif value == 90:
            self.image = (
                (b, d),
                (a, c)
            )

    def setUp(self):
        self.image = (
            (1, 2),
            (3, 4)
        )
        self.context = self.get_context()
        self.engine = BaseEngine(self.context)
        self.engine.flip_horizontally = mock.MagicMock()
        self.engine.flip_horizontally.side_effect = self.flip_horizontally
        self.engine.flip_vertically = mock.MagicMock()
        self.engine.flip_vertically.side_effect = self.flip_vertically
        self.engine.rotate = mock.MagicMock()
        self.engine.rotate.side_effect = self.rotate

    def test_create_engine(self):
        expect(self.engine).to_be_instance_of(BaseEngine)

    def test_convert_svg_to_png(self):
        buffer = """<svg width="10px" height="20px" viewBox="0 0 10 20"
                    xmlns="http://www.w3.org/2000/svg">
                        <rect width="100%" height="10" x="0" y="0"/>
                    </svg>"""
        self.engine.convert_svg_to_png(buffer)
        expect(self.engine.extension).to_equal('.png')

    @mock.patch('thumbor.engines.cairosvg', new=None)
    @mock.patch('thumbor.engines.logger.error')
    def test_not_imported_cairosvg_failed_to_convert_svg_to_png(self, mockLogError):
        buffer = """<svg width="10px" height="20px" viewBox="0 0 10 20"
                    xmlns="http://www.w3.org/2000/svg">
                        <rect width="100%" height="10" x="0" y="0"/>
                    </svg>"""
        returned_buffer = self.engine.convert_svg_to_png(buffer)
        expect(mockLogError.called).to_be_true()
        expect(buffer).to_equal(returned_buffer)

    def test_get_orientation(self):
        self.engine.exif = exif_str(1)
        expect(self.engine.get_orientation()).to_equal(1)
        expect(self.engine.get_orientation()).to_equal(1)
        self.engine.exif = exif_str(6)
        expect(self.engine.get_orientation()).to_equal(6)
        expect(self.engine.get_orientation()).to_equal(6)
        self.engine.exif = exif_str(8)
        expect(self.engine.get_orientation()).to_equal(8)
        expect(self.engine.get_orientation()).to_equal(8)

    def test_reorientate1(self):
        # No rotation
        self.engine.exif = exif_str(1)
        self.engine.reorientate()
        expect(self.engine.rotate.called).to_be_false()
        expect(self.engine.flip_horizontally.called).to_be_false()
        expect(self.engine.flip_vertically.called).to_be_false()
        expect(self.image).to_equal(((1, 2), (3, 4)))

        expect(self.engine.get_orientation()).to_equal(1)

    def test_reorientate2(self):
        self.image = (
            (2, 1),
            (4, 3)
        )
        # Flipped horizontally
        self.engine.exif = exif_str(2)
        self.engine.reorientate()
        expect(self.engine.rotate.called).to_be_false()
        expect(self.engine.flip_horizontally.called).to_be_true()
        expect(self.engine.flip_vertically.called).to_be_false()
        expect(self.image).to_equal(((1, 2), (3, 4)))

        expect(self.engine.get_orientation()).to_equal(1)

    def test_reorientate3(self):
        # Rotated 180°  Ⅎ
        self.image = (
            (4, 3),
            (2, 1)
        )
        self.engine.exif = exif_str(3)
        self.engine.reorientate()
        expect(self.engine.rotate.call_args[0]).to_equal((180,))
        expect(self.engine.flip_horizontally.called).to_be_false()
        expect(self.engine.flip_vertically.called).to_be_false()
        expect(self.image).to_equal(((1, 2), (3, 4)))

        expect(self.engine.get_orientation()).to_equal(1)

    def test_reorientate4(self):
        # Flipped vertically
        self.image = (
            (3, 4),
            (1, 2)
        )
        self.engine.exif = exif_str(4)
        self.engine.reorientate()
        expect(self.engine.rotate.called).to_be_false()
        expect(self.engine.flip_horizontally.called).to_be_false()
        expect(self.engine.flip_vertically.called).to_be_true()
        expect(self.image).to_equal(((1, 2), (3, 4)))

        expect(self.engine.get_orientation()).to_equal(1)

    def test_reorientate5(self):
        # Horizontal Mirror + Rotation 270
        # or Vertical Mirror + Rotation 90
        self.image = (
            (1, 3),
            (2, 4)
        )
        self.engine.exif = exif_str(5)
        self.engine.reorientate()
        expect(self.image).to_equal(((1, 2), (3, 4)))

        expect(self.engine.get_orientation()).to_equal(1)

    def test_reorientate6(self):
        # Rotate 270°
        self.image = (
            (2, 4),
            (1, 3)
        )
        self.engine.exif = exif_str(6)
        self.engine.reorientate()
        expect(self.engine.rotate.call_args[0]).to_equal((270,))
        expect(self.engine.flip_horizontally.called).to_be_false()
        expect(self.engine.flip_vertically.called).to_be_false()
        expect(self.image).to_equal(((1, 2), (3, 4)))

        expect(self.engine.get_orientation()).to_equal(1)

    def test_reorientate7(self):
        # Flipped horizontally and rotate 90°
        self.image = (
            (4, 2),
            (3, 1)
        )
        self.engine.exif = exif_str(7)
        self.engine.reorientate()
        expect(self.image).to_equal(((1, 2), (3, 4)))

        expect(self.engine.get_orientation()).to_equal(1)

    def test_reorientate8(self):
        # Rotate 90°
        self.image = (
            (3, 1),
            (4, 2)
        )
        self.engine.exif = exif_str(8)
        self.engine.reorientate()
        expect(self.engine.rotate.call_args[0]).to_equal((90,))
        expect(self.engine.flip_horizontally.called).to_be_false()
        expect(self.engine.flip_vertically.called).to_be_false()
        expect(self.image).to_equal(((1, 2), (3, 4)))

        expect(self.engine.get_orientation()).to_equal(1)
