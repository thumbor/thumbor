# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import builtins
import importlib.util
from io import BytesIO
from os.path import abspath, dirname, join
from struct import pack
from unittest import TestCase, mock
from xml.etree.ElementTree import ParseError

import cairosvg
import pytest
from PIL import Image

import thumbor.engines
from thumbor.config import Config
from thumbor.context import Context, RequestParameters
from thumbor.engines import BaseEngine, svg_document_size
from thumbor.filters import FiltersFactory, no_upscale
from thumbor.point import FocalPoint
from thumbor.url import Url

# pylint: disable=line-too-long

STORAGE_PATH = abspath(join(dirname(__file__), "../fixtures/images/"))


@pytest.mark.parametrize("error_type", [ImportError, OSError])
def test_can_import_engine_without_cairo(error_type):
    original_import = builtins.__import__
    error = error_type("cannot load library libcairo-2.dll")

    def import_without_cairo(name, *args, **kwargs):
        if name == "cairosvg":
            raise error
        return original_import(name, *args, **kwargs)

    spec = importlib.util.spec_from_file_location(
        "engine_without_cairo", thumbor.engines.__file__
    )
    engine_module = importlib.util.module_from_spec(spec)
    with mock.patch("builtins.__import__", side_effect=import_without_cairo):
        spec.loader.exec_module(engine_module)

    assert engine_module.cairosvg is None
    assert engine_module.CAIROSVG_IMPORT_ERROR is error


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
        (first, second), (third, fourth) = self.image
        self.image = ((second, first), (fourth, third))

    def flip_vertically(self):
        (first, second), (third, fourth) = self.image
        self.image = ((third, fourth), (first, second))

    def rotate(self, value):
        (first, second), (third, fourth) = self.image
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
        assert isinstance(self.engine, BaseEngine)

    def test_convert_svg_to_png(self):
        buffer = """<svg width="10px" height="20px" viewBox="0 0 10 20"
                    xmlns="http://www.w3.org/2000/svg">
                        <rect width="100%" height="10" x="0" y="0"/>
                    </svg>"""
        self.engine.convert_svg_to_png(buffer)
        assert self.engine.extension == ".png"

    def test_convert_svg_with_xml_preamble_to_png(self):
        buffer = """<?xml version="1.0" encoding="utf-8"?>
                    <svg width="10px" height="20px" viewBox="0 0 10 20"
                    xmlns="http://www.w3.org/2000/svg">
                        <rect width="100%" height="10" x="0" y="0"/>
                    </svg>""".encode("utf-8")
        self.engine.convert_svg_to_png(buffer)
        assert self.engine.extension == ".png"

    def test_convert_svg_utf16_to_png(self):
        buffer = """<?xml version="1.0" encoding="utf-16"?>
                    <svg width="10px" height="20px" viewBox="0 0 10 20"
                    xmlns="http://www.w3.org/2000/svg">
                        <rect width="100%" height="10" x="0" y="0"/>
                    </svg>""".encode("utf-16")
        self.engine.convert_svg_to_png(buffer)
        assert self.engine.extension == ".png"

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
        assert mock_log_error.called
        assert returned_buffer == buffer

    @mock.patch("thumbor.engines.cairosvg", new=None)
    @mock.patch("thumbor.engines.logger.error")
    def test_cairo_load_error_is_logged_when_svg_conversion_is_unavailable(
        self, mock_log_error
    ):
        error = OSError("cannot load library libcairo-2.dll")
        buffer = b"<svg/>"

        with mock.patch("thumbor.engines.CAIROSVG_IMPORT_ERROR", new=error):
            assert self.engine.convert_svg_to_png(buffer) == buffer

        mock_log_error.assert_called_once_with(mock.ANY, error)

    def test_can_identify_msb_tiff(self):
        with open(
            join(STORAGE_PATH, "gradient_msb_16bperchannel.tif"), "rb"
        ) as image:
            buffer = image.read()
        mime = self.engine.get_mimetype(buffer)
        assert mime == "image/tiff"

    def test_can_identify_lsb_tiff(self):
        with open(
            join(STORAGE_PATH, "gradient_lsb_16bperchannel.tif"), "rb"
        ) as image:
            buffer = image.read()
        mime = self.engine.get_mimetype(buffer)
        assert mime == "image/tiff"

    def test_can_identify_svg_with_xml_namespace_other_than_w3(self):
        buffer = b"""<svg width="10px" height="20px" viewBox="0 0 10 20"
                    xmlns="http://ns.foo.com/FooSVGViewerExtensions/3.0/">
                        <rect width="100%" height="10" x="0" y="0"/>
                    </svg>"""
        mime = self.engine.get_mimetype(buffer)
        assert mime == "image/svg+xml"

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
        assert mime == "image/svg+xml"

    def test_can_identify_avif(self):
        with open(join(STORAGE_PATH, "image.avif"), "rb") as image:
            buffer = image.read()
        mime = self.engine.get_mimetype(buffer)
        assert mime == "image/avif"

    def test_can_identify_heic(self):
        with open(join(STORAGE_PATH, "image.heic"), "rb") as image:
            buffer = image.read()
        mime = self.engine.get_mimetype(buffer)
        assert mime == "image/heif"

    def test_convert_svg_already_converted_to_png(self):
        svg_buffer = """<svg width="10px" height="20px" viewBox="0 0 10 20"
                    xmlns="http://www.w3.org/2000/svg">
                        <rect width="100%" height="10" x="0" y="0"/>
                    </svg>"""
        png_buffer = self.engine.convert_svg_to_png(svg_buffer)
        png_buffer_dupe = self.engine.convert_svg_to_png(png_buffer)
        assert self.engine.extension == ".png"
        assert png_buffer == png_buffer_dupe

    def test_convert_not_well_formed_svg_to_png(self):
        buffer = b"""<<svg width="10px" height="20px" viewBox="0 0 10 20"
                    xmlns="http://www.w3.org/2000/svg">
                        <rect width="100%" height="10" x="0" y="0"/>
                    </svg>"""
        with pytest.raises(ParseError):
            self.engine.convert_svg_to_png(buffer)
        assert self.engine.extension is None

    def test_get_orientation_no_exif(self):
        assert not hasattr(self.engine, "exif")
        assert self.engine.get_orientation() is None

    def test_get_orientation_null_exif(self):
        self.engine.exif = None
        assert self.engine.get_orientation() is None

    def test_get_orientation_without_orientation_in_exif(self):
        self.engine.exif = b"Exif\x00\x00II*\x00\x08\x00\x00\x00\x01\x00\x1a\x01\x05\x00\x01\x00\x00\x006\x00\x00\x00"
        assert self.engine.get_orientation() is None

    def test_get_orientation(self):
        self.engine.exif = exif_str(1)
        assert self.engine.get_orientation() == 1
        assert self.engine.get_orientation() == 1
        self.engine.exif = exif_str(6)
        assert self.engine.get_orientation() == 6
        assert self.engine.get_orientation() == 6
        self.engine.exif = exif_str(8)
        assert self.engine.get_orientation() == 8
        assert self.engine.get_orientation() == 8

    def test_reorientate_no_exif(self):
        assert not hasattr(self.engine, "exif")
        self.engine.reorientate()
        assert self.engine.get_orientation() is None

    def test_reorientate_null_exif(self):
        self.engine.exif = None
        self.engine.reorientate()
        assert self.engine.get_orientation() is None

    def test_reorientate1(self):
        self.engine.exif = exif_str(1)
        self.engine.reorientate()
        assert not self.engine.rotate.called
        assert not self.engine.flip_horizontally.called
        assert not self.engine.flip_vertically.called
        assert self.image == ((1, 2), (3, 4))
        assert self.engine.get_orientation() == 1

    def test_reorientate2(self):
        self.image = ((2, 1), (4, 3))
        self.engine.exif = exif_str(2)
        self.engine.reorientate()
        assert not self.engine.rotate.called
        assert self.engine.flip_horizontally.called
        assert not self.engine.flip_vertically.called
        assert self.image == ((1, 2), (3, 4))
        assert self.engine.get_orientation() == 1

    def test_reorientate3(self):
        self.image = ((4, 3), (2, 1))
        self.engine.exif = exif_str(3)
        self.engine.reorientate()
        assert self.engine.rotate.call_args[0] == (180,)
        assert not self.engine.flip_horizontally.called
        assert not self.engine.flip_vertically.called
        assert self.image == ((1, 2), (3, 4))
        assert self.engine.get_orientation() == 1

    def test_reorientate4(self):
        self.image = ((3, 4), (1, 2))
        self.engine.exif = exif_str(4)
        self.engine.reorientate()
        assert not self.engine.rotate.called
        assert not self.engine.flip_horizontally.called
        assert self.engine.flip_vertically.called
        assert self.image == ((1, 2), (3, 4))
        assert self.engine.get_orientation() == 1

    def test_reorientate5(self):
        self.image = ((1, 3), (2, 4))
        self.engine.exif = exif_str(5)
        self.engine.reorientate()
        assert self.image == ((1, 2), (3, 4))
        assert self.engine.get_orientation() == 1

    def test_reorientate6(self):
        self.image = ((2, 4), (1, 3))
        self.engine.exif = exif_str(6)
        self.engine.reorientate()
        assert self.engine.rotate.call_args[0] == (270,)
        assert not self.engine.flip_horizontally.called
        assert not self.engine.flip_vertically.called
        assert self.image == ((1, 2), (3, 4))
        assert self.engine.get_orientation() == 1

    def test_reorientate7(self):
        self.image = ((4, 2), (3, 1))
        self.engine.exif = exif_str(7)
        self.engine.reorientate()
        assert self.image == ((1, 2), (3, 4))
        assert self.engine.get_orientation() == 1

    def test_reorientate8(self):
        self.image = ((3, 1), (4, 2))
        self.engine.exif = exif_str(8)
        self.engine.reorientate()
        assert self.engine.rotate.call_args[0] == (90,)
        assert not self.engine.flip_horizontally.called
        assert not self.engine.flip_vertically.called
        assert self.image == ((1, 2), (3, 4))
        assert self.engine.get_orientation() == 1


RED_BLUE_SVG = (
    b'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="100" '
    b'viewBox="0 0 200 100"><rect width="100" height="100" fill="#ff0000"/>'
    b'<rect x="100" width="100" height="100" fill="#0000ff"/></svg>'
)
RED = (255, 0, 0, 255)
BLUE = (0, 0, 255, 255)


def svg_request(url):
    return RequestParameters(**Url.parse_decrypted(url))


def svg_engine(request, filters=(no_upscale.Filter,), **config):
    context = Context(
        config=Config(
            SECURITY_KEY="ACME-SEC", ENGINE="thumbor.engines", **config
        )
    )
    context.filters_factory = FiltersFactory(filters)
    context.request = request
    engine = BaseEngine(context)
    request.engine = engine
    return engine


def rasterize(engine, buffer=RED_BLUE_SVG):
    png = engine.convert_svg_to_png(buffer)
    assert engine.extension == ".png"
    return Image.open(BytesIO(png)).convert("RGBA")


@pytest.mark.parametrize(
    "url, expected_size",
    [
        ("/fit-in/100x100/red-blue.svg", (100, 50)),
        ("/fit-in/400x400/red-blue.svg", (400, 200)),
        ("/fit-in/400x400/filters:no_upscale()/red-blue.svg", (200, 100)),
        (
            "/fit-in/400x400/filters:format(png):no_upscale()/red-blue.svg",
            (200, 100),
        ),
        (
            "/fit-in/400x400/filters:watermark(no_upscale().svg,0,0,0)/red-blue.svg",
            (400, 200),
        ),
        ("/full-fit-in/400x400/red-blue.svg", (800, 400)),
        ("/adaptive-fit-in/100x200/red-blue.svg", (200, 100)),
        ("/400x400/filters:stretch()/red-blue.svg", (800, 400)),
        ("/400x400/filters:no_upscale()/red-blue.svg", (200, 100)),
        ("/100x100/red-blue.svg", (200, 100)),
        ("/400x400/red-blue.svg", (800, 400)),
        ("/100x0/red-blue.svg", (100, 50)),
        ("/0x0/red-blue.svg", (200, 100)),
        ("/origx100/red-blue.svg", (200, 100)),
    ],
)
def test_svg_is_drawn_at_the_size_the_transforms_need(url, expected_size):
    image = rasterize(svg_engine(svg_request(url)))

    width, height = image.size
    assert image.size == expected_size
    assert image.getpixel((0, 0)) == RED
    assert image.getpixel((width - 1, height - 1)) == BLUE


@pytest.mark.parametrize(
    "url, expected_size, expected_request_size",
    [
        ("/origx400/red-blue.svg", (800, 400), (200, 400)),
        ("/400xorig/red-blue.svg", (400, 200), (400, 100)),
        ("/10x10:110x60/400xorig/red-blue.svg", (800, 400), (400, 50)),
        ("/fit-in/origx50/red-blue.svg", (100, 50), (200, 50)),
        ("/origxorig/red-blue.svg", (200, 100), ("orig", "orig")),
    ],
)
def test_svg_orig_means_the_document_size(
    url, expected_size, expected_request_size
):
    request = svg_request(url)

    image = rasterize(svg_engine(request))

    assert image.size == expected_size
    assert (request.width, request.height) == expected_request_size


def test_svg_crop_and_focal_points_follow_the_raster_scale():
    request = svg_request("/10x10:110x60/200x100/red-blue.svg")
    request.focal_points.append(FocalPoint.from_square(150, 0, 50, 100))

    image = rasterize(svg_engine(request))

    assert image.size == (400, 200)
    assert request.crop == {"left": 20, "top": 20, "right": 220, "bottom": 120}
    point = request.focal_points[0]
    assert (point.x, point.y, point.width, point.height) == (
        350,
        100,
        100,
        200,
    )
    assert point.weight == 20000


def test_svg_ignores_no_upscale_when_the_filter_is_not_registered():
    request = svg_request("/fit-in/400x400/filters:no_upscale()/red-blue.svg")

    assert rasterize(svg_engine(request, filters=())).size == (400, 200)


def test_svg_accepts_a_request_whose_filters_are_a_list():
    request = RequestParameters(width=400, height=400)

    assert rasterize(svg_engine(request)).size == (800, 400)


@pytest.mark.parametrize(
    "config, expected_size",
    [({"MAX_WIDTH": 1000}, (1000, 500)), ({"MAX_HEIGHT": 100}, (200, 100))],
)
def test_svg_raster_stays_within_max_width_and_height(config, expected_size):
    engine = svg_engine(svg_request("/1000x1000/red-blue.svg"), **config)

    assert rasterize(engine).size == expected_size


@pytest.mark.parametrize(
    "url, config, expected_size, expected_request_size",
    [
        ("/origxorig/red-blue.svg", {"MAX_WIDTH": 100}, (100, 50), (100, 50)),
        ("/origx20/red-blue.svg", {"MAX_WIDTH": 100}, (100, 50), (100, 20)),
        ("/400xorig/red-blue.svg", {"MAX_HEIGHT": 50}, (100, 50), (400, 50)),
        (
            "/10x10:110x60/origxorig/red-blue.svg",
            {"MAX_WIDTH": 100},
            (100, 50),
            (50, 25),
        ),
        (
            "/origxorig/red-blue.svg",
            {"MAX_PIXELS": 5000},
            (100, 50),
            (100, 50),
        ),
    ],
)
def test_svg_orig_follows_the_size_limits(
    url, config, expected_size, expected_request_size
):
    request = svg_request(url)

    image = rasterize(svg_engine(request, **config))

    assert image.size == expected_size
    assert (request.width, request.height) == expected_request_size


@pytest.mark.parametrize("max_pixels", [0, "abc"])
def test_svg_raster_uses_pillows_limit_when_max_pixels_is_unusable(
    max_pixels,
):
    engine = svg_engine(
        svg_request("/400x400/red-blue.svg"), MAX_PIXELS=max_pixels
    )

    with mock.patch.object(Image, "MAX_IMAGE_PIXELS", 10000):
        assert rasterize(engine).size == (140, 70)


def test_svg_one_pixel_floor_falls_back_to_the_request_box():
    banner = (
        b'<svg xmlns="http://www.w3.org/2000/svg" width="5000" height="1">'
        b'<rect width="100%" height="100%" fill="#f00"/></svg>'
    )
    engine = svg_engine(svg_request("/100x100/banner.svg"), MAX_WIDTH=1000)

    assert rasterize(engine, banner).size == (100, 100)


@pytest.mark.parametrize(
    "url, max_pixels, expected_size",
    [
        ("/400x400/red-blue.svg", None, (800, 400)),
        ("/400x400/red-blue.svg", 80000, (400, 200)),
        ("/400x400/red-blue.svg", 79999, (399, 200)),
        ("/400x400/red-blue.svg", 10000, (140, 70)),
        ("/0x0/red-blue.svg", 10000, (140, 70)),
    ],
)
def test_svg_raster_stays_within_max_pixels(url, max_pixels, expected_size):
    engine = svg_engine(svg_request(url), MAX_PIXELS=max_pixels)

    assert rasterize(engine).size == expected_size


@pytest.mark.parametrize(
    "width, height, url, expected_size",
    [
        (20000, 10, "/1000x1000/banner.svg", (32767, 16)),
        (20000, 10, "/fit-in/1000x1000/banner.svg", (2000, 1)),
        (33000, 10, "/100x100/banner.svg", (32767, 10)),
        (33000, 10, "/0x0/banner.svg", (32767, 10)),
        (1, 40000, "/100x100/banner.svg", (100, 100)),
    ],
)
def test_svg_with_an_extreme_aspect_ratio_stays_drawable(
    width, height, url, expected_size
):
    banner = (
        b'<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d">'
        b'<rect width="100%%" height="100%%" fill="#f00"/></svg>'
        % (width, height)
    )
    engine = svg_engine(svg_request(url))

    assert rasterize(engine, banner).size == expected_size


def test_svg_without_a_request_is_drawn_at_the_document_size():
    context = Context(
        config=Config(SECURITY_KEY="ACME-SEC", ENGINE="thumbor.engines")
    )

    assert rasterize(BaseEngine(context)).size == (200, 100)


def test_svg_loaded_by_another_engine_keeps_the_document_size():
    engine = svg_engine(svg_request("/400x400/red-blue.svg"))
    watermark_engine = BaseEngine(engine.context)

    assert rasterize(watermark_engine).size == (200, 100)


@pytest.mark.parametrize(
    "max_pixels, expected_size", [(None, (300, 200)), (10000, (121, 81))]
)
def test_svg_without_a_size_is_drawn_at_the_requested_box(
    max_pixels, expected_size
):
    engine = svg_engine(
        svg_request("/300x200/no-size.svg"), MAX_PIXELS=max_pixels
    )
    sizeless = (
        b'<svg xmlns="http://www.w3.org/2000/svg">'
        b'<rect width="50" height="50"/></svg>'
    )

    assert rasterize(engine, sizeless).size == expected_size


@pytest.mark.parametrize(
    "declaration",
    [
        'width="2in" height="1in"',
        'width="20em" height="10em"',
        'width="100mm" height="50mm"',
        'width="100%" height="100%" viewBox="0 0 40 20"',
        'viewBox="0 0 40 20"',
    ],
)
@pytest.mark.parametrize("dpi", [72, 150])
def test_svg_document_size_matches_what_cairosvg_draws(declaration, dpi):
    document = (
        f'<svg xmlns="http://www.w3.org/2000/svg" {declaration}>'
        '<rect width="100%" height="100%" fill="#f00"/></svg>'
    ).encode()
    drawn = Image.open(BytesIO(cairosvg.svg2png(bytestring=document, dpi=dpi)))

    tree = thumbor.engines.svg_parser.Tree(bytestring=document)
    width, height = svg_document_size(tree, dpi)

    assert (round(width), round(height)) == drawn.size
