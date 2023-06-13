#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

# pylint: disable=line-too-long

from os.path import abspath, dirname, join
from struct import pack
from unittest import TestCase, mock
from xml.etree.ElementTree import ParseError

from preggy import expect

from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines import BaseEngine

STORAGE_PATH = abspath(join(dirname(__file__), "../fixtures/images/"))


def exif_str(exif_value):
    return (
        b"Exif\x00\x00II*\x00\x08\x00\x00\x00\x05\x00\x12\x01\x03\x00\x01\x00\x00\x00%s\x00\x00\x1a\x01\x05\x00\x01\x00\x00\x00J\x00\x00\x00\x1b\x01\x05\x00\x01\x00\x00\x00R\x00\x00\x00(\x01\x03\x00\x01\x00\x00\x00\x02\x00\x00\x00\x13\x02\x03\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00H\x00\x00\x00\x01\x00\x00\x00H\x00\x00\x00\x01\x00\x00\x00"  # pylint: disable=line-too-long
        % pack("<h", exif_value)
    )  # noqa


class BaseEngineTestCase(TestCase):
    def get_context(self):
        cfg = Config(
            SECURITY_KEY="ACME-SEC",
            ENGINE="thumbor.engines",
        )
        cfg.STORAGE = "thumbor.storages.no_storage"

        return Context(config=cfg)

    def flip_horizontally(self):
        ((first, second), (third, fourth)) = self.image
        self.image = ((second, first), (fourth, third))

    def flip_vertically(self):
        ((first, second), (third, fourth)) = self.image
        self.image = ((third, fourth), (first, second))

    def rotate(self, value):
        ((first, second), (third, fourth)) = self.image
        if value == 270:
            self.image = ((third, first), (fourth, second))
        elif value == 180:
            self.image = ((fourth, third), (second, first))
        elif value == 90:
            self.image = ((second, fourth), (first, third))

    def setUp(self):
        self.image = ((1, 2), (3, 4))
        self.context = self.get_context()
        self.context.request = mock.MagicMock(width=0, height=0)
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
        expect(self.engine.extension).to_equal(".png")

    def test_convert_svg_with_xml_preamble_to_png(self):
        buffer = """<?xml version="1.0" encoding="utf-8"?>
                    <svg width="10px" height="20px" viewBox="0 0 10 20"
                    xmlns="http://www.w3.org/2000/svg">
                        <rect width="100%" height="10" x="0" y="0"/>
                    </svg>""".encode(
            "utf-8"
        )
        self.engine.convert_svg_to_png(buffer)
        expect(self.engine.extension).to_equal(".png")

    def test_convert_svg_utf16_to_png(self):
        buffer = """<?xml version="1.0" encoding="utf-16"?>
                    <svg width="10px" height="20px" viewBox="0 0 10 20"
                    xmlns="http://www.w3.org/2000/svg">
                        <rect width="100%" height="10" x="0" y="0"/>
                    </svg>""".encode(
            "utf-16"
        )
        self.engine.convert_svg_to_png(buffer)
        expect(self.engine.extension).to_equal(".png")

    @mock.patch("thumbor.engines.cairosvg", new=None)
    @mock.patch("thumbor.engines.logger.error")
    def test_not_imported_cairosvg_failed_to_convert_svg_to_png(
        self, mock_log_error
    ):
        buffer = """<svg width="10px" height="20px" viewBox="0 0 10 20"
                    xmlns="http://www.w3.org/2000/svg">
                        <rect width="100%" height="10" x="0" y="0"/>
                    </svg>"""
        returned_buffer = self.engine.convert_svg_to_png(buffer)
        expect(mock_log_error.called).to_be_true()
        expect(buffer).to_equal(returned_buffer)

    def test_can_identify_msb_tiff(self):
        with open(
            join(STORAGE_PATH, "gradient_msb_16bperchannel.tif"), "rb"
        ) as image:
            buffer = image.read()
        mime = self.engine.get_mimetype(buffer)
        expect(mime).to_equal("image/tiff")

    def test_can_identify_lsb_tiff(self):
        with open(
            join(STORAGE_PATH, "gradient_lsb_16bperchannel.tif"), "rb"
        ) as image:
            buffer = image.read()
        mime = self.engine.get_mimetype(buffer)
        expect(mime).to_equal("image/tiff")

    def test_can_identify_svg_with_xml_namespace_other_than_w3(self):
        buffer = b"""<svg width="10px" height="20px" viewBox="0 0 10 20"
                    xmlns="http://ns.foo.com/FooSVGViewerExtensions/3.0/">
                        <rect width="100%" height="10" x="0" y="0"/>
                    </svg>"""
        mime = self.engine.get_mimetype(buffer)
        expect(mime).to_equal("image/svg+xml")

    def test_can_identify_svg_with_xml_preamble_and_lots_of_gibberish(self):
        buffer = b"""<?xml version="1.0" encoding="utf-8"?>
                    <!-- Generator: Proprietary Drawing Software, SVG Export Plug-In. SVG Version: 3.0.0 Build 77) -->
                    <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//ENhttp://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd" [
                        <!ENTITY ns_flows "http://ns.foo.com/Flows/1.0/">
                        <!ENTITY ns_extend "http://ns.foo.com/Extensibility/1.0/">
                        <!ENTITY ns_ai "http://ns.foo.com/foobar/10.0/">
                        <!ENTITY ns_graphs "http://ns.foo.com/Graphs/1.0/">
                        <!ENTITY ns_vars "http://ns.foo.com/Variables/1.0/">
                        <!ENTITY ns_imrep "http://ns.foo.com/ImageReplacement/1.0/">
                        <!ENTITY ns_sfw "http://ns.foo.com/SaveForWeb/1.0/">
                        <!ENTITY ns_custom "http://ns.foo.com/GenericCustomNamespace/1.0/">
                        <!ENTITY ns_foo_xpath "http://ns.foo.com/XPath/1.0/">
                        <!ENTITY ns_svg "http://www.w3.org/2000/svg">
                        <!ENTITY ns_xlink "http://www.w3.org/1999/xlink">
                    ]>
                    <svg width="10px" height="20px" viewBox="0 0 10 20"
                    xmlns="http://www.w3.org/2000/svg">
                        <rect width="100%" height="10" x="0" y="0"/>
                    </svg>"""
        mime = self.engine.get_mimetype(buffer)
        expect(mime).to_equal("image/svg+xml")

    def test_can_identify_avif(self):
        with open(join(STORAGE_PATH, "image.avif"), "rb") as image:
            buffer = image.read()
        mime = self.engine.get_mimetype(buffer)
        expect(mime).to_equal("image/avif")

    def test_can_identify_heic(self):
        with open(join(STORAGE_PATH, "image.heic"), "rb") as image:
            buffer = image.read()
        mime = self.engine.get_mimetype(buffer)
        expect(mime).to_equal("image/heif")

    def test_convert_svg_already_converted_to_png(self):
        svg_buffer = """<svg width="10px" height="20px" viewBox="0 0 10 20"
                    xmlns="http://www.w3.org/2000/svg">
                        <rect width="100%" height="10" x="0" y="0"/>
                    </svg>"""
        png_buffer = self.engine.convert_svg_to_png(svg_buffer)
        png_buffer_dupe = self.engine.convert_svg_to_png(png_buffer)
        expect(self.engine.extension).to_equal(".png")
        expect(png_buffer).to_equal(png_buffer_dupe)

    def test_convert_not_well_formed_svg_to_png(self):
        buffer = b"""<<svg width="10px" height="20px" viewBox="0 0 10 20"
                    xmlns="http://www.w3.org/2000/svg">
                        <rect width="100%" height="10" x="0" y="0"/>
                    </svg>"""
        with expect.error_to_happen(ParseError):
            self.engine.convert_svg_to_png(buffer)
        expect(self.engine.extension).to_be_null()

    def test_get_orientation_no_exif(self):
        expect(hasattr(self.engine, "exif")).to_be_false()
        expect(self.engine.get_orientation()).to_be_null()

    def test_get_orientation_null_exif(self):
        self.engine.exif = None
        expect(self.engine.get_orientation()).to_be_null()

    def test_get_orientation_without_orientation_in_exif(self):
        self.engine.exif = b"Exif\x00\x00II*\x00\x08\x00\x00\x00\x01\x00\x1a\x01\x05\x00\x01\x00\x00\x006\x00\x00\x00"
        expect(self.engine.get_orientation()).to_be_null()

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

    def test_reorientate_no_exif(self):
        expect(hasattr(self.engine, "exif")).to_be_false()
        self.engine.reorientate()
        expect(self.engine.get_orientation()).to_be_null()

    def test_reorientate_null_exif(self):
        self.engine.exif = None
        self.engine.reorientate()
        expect(self.engine.get_orientation()).to_be_null()

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
        self.image = ((2, 1), (4, 3))
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
        self.image = ((4, 3), (2, 1))
        self.engine.exif = exif_str(3)
        self.engine.reorientate()
        expect(self.engine.rotate.call_args[0]).to_equal((180,))
        expect(self.engine.flip_horizontally.called).to_be_false()
        expect(self.engine.flip_vertically.called).to_be_false()
        expect(self.image).to_equal(((1, 2), (3, 4)))

        expect(self.engine.get_orientation()).to_equal(1)

    def test_reorientate4(self):
        # Flipped vertically
        self.image = ((3, 4), (1, 2))
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
        self.image = ((1, 3), (2, 4))
        self.engine.exif = exif_str(5)
        self.engine.reorientate()
        expect(self.image).to_equal(((1, 2), (3, 4)))

        expect(self.engine.get_orientation()).to_equal(1)

    def test_reorientate6(self):
        # Rotate 270°
        self.image = ((2, 4), (1, 3))
        self.engine.exif = exif_str(6)
        self.engine.reorientate()
        expect(self.engine.rotate.call_args[0]).to_equal((270,))
        expect(self.engine.flip_horizontally.called).to_be_false()
        expect(self.engine.flip_vertically.called).to_be_false()
        expect(self.image).to_equal(((1, 2), (3, 4)))

        expect(self.engine.get_orientation()).to_equal(1)

    def test_reorientate7(self):
        # Flipped horizontally and rotate 90°
        self.image = ((4, 2), (3, 1))
        self.engine.exif = exif_str(7)
        self.engine.reorientate()
        expect(self.image).to_equal(((1, 2), (3, 4)))

        expect(self.engine.get_orientation()).to_equal(1)

    def test_reorientate8(self):
        # Rotate 90°
        self.image = ((3, 1), (4, 2))
        self.engine.exif = exif_str(8)
        self.engine.reorientate()
        expect(self.engine.rotate.call_args[0]).to_equal((90,))
        expect(self.engine.flip_horizontally.called).to_be_false()
        expect(self.engine.flip_vertically.called).to_be_false()
        expect(self.image).to_equal(((1, 2), (3, 4)))

        expect(self.engine.get_orientation()).to_equal(1)
