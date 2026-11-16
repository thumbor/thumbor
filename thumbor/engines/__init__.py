# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

# This is a base class, it makes sense to have many public methods and instance attributes
# pylint: disable=attribute-defined-outside-init,too-many-public-methods,unused-argument,too-many-instance-attributes,broad-except

import math
import re
from io import BytesIO
from types import SimpleNamespace
from xml.etree.ElementTree import ParseError

import piexif
from PIL import Image

from thumbor.engines.extensions.exif_orientation_editor import (
    ExifOrientationEditor,
)
from thumbor.utils import EXTENSION, logger

try:
    import cairosvg
    from cairosvg import helpers as svg_helpers
    from cairosvg import parser as svg_parser
    from cairosvg import surface as svg_surface
except (ImportError, OSError) as error:
    cairosvg = svg_helpers = svg_parser = svg_surface = None
    CAIROSVG_IMPORT_ERROR = error
else:
    CAIROSVG_IMPORT_ERROR = None


WEBP_SIDE_LIMIT = 16383
CAIRO_SIDE_LIMIT = 32767

SVG_RE = re.compile(rb"<svg\b[^>]*?>", re.I)
NO_UPSCALE_FILTER_RE = re.compile(r"(?:^|\):)no_upscale\(\)")


def svg_document_size(tree, dpi):
    """Size, in pixels at ``dpi``, that CairoSVG draws the document at
    when no output size is requested."""
    viewport = SimpleNamespace(
        dpi=dpi, context_width=None, context_height=None
    )
    viewport.font_size = svg_helpers.size(viewport, "12pt")
    width, height, _ = svg_helpers.node_format(viewport, tree)
    return width, height


def _svg_raster_size(svg_width, svg_height, scale):
    output_width = svg_width * scale
    return round(output_width), round(svg_height * (output_width / svg_width))


def _svg_raster_pixels(svg_width, svg_height, scale):
    width, height = _svg_raster_size(svg_width, svg_height, scale)
    return width * height


def _max_pixels(config):
    max_pixels = config.MAX_PIXELS
    if max_pixels is None:
        return None
    try:
        if int(max_pixels):
            return max_pixels
    except (TypeError, ValueError):
        pass
    # The PIL engine leaves Pillow's own limit in place for zero and for
    # values it cannot read.
    return Image.MAX_IMAGE_PIXELS


def _requested_pixels(dimension):
    if isinstance(dimension, int) and dimension > 0:
        return dimension
    return None


def _orientation_differs(source_width, source_height, width, height):
    return (source_width < source_height and width > height) or (
        source_width > source_height and width < height
    )


class EngineResult:
    COULD_NOT_LOAD_IMAGE = "could not load image"

    def __init__(
        self, buffer_=None, successful=True, error=None, metadata=None
    ):
        """
        :param buffer: The media buffer

        :param successful: True when the media has been read by the engine.
        :type successful: bool

        :param error: Error code
        :type error: str

        :param metadata: Dictionary of metadata about the buffer
        :type metadata: dict
        """

        if metadata is None:
            metadata = {}

        self.buffer = buffer_
        self.successful = successful
        self.error = error
        self.metadata = metadata


class MultipleEngine:
    def __init__(self, source_engine):
        self.frame_engines = []
        self.source_engine = source_engine

    def add_frame(self, frame):
        frame_engine = self.source_engine.__class__(self.source_engine.context)
        frame_engine.extension = self.source_engine.extension
        frame_engine.source_width = self.source_engine.source_width
        frame_engine.source_height = self.source_engine.source_height
        frame_engine.image = frame

        self.frame_engines.append(frame_engine)

    def read(self, extension=None, quality=None):
        return self.source_engine.read_multiple(
            [frame_engine.image for frame_engine in self.frame_engines],
            extension,
        )

    def size(self):
        return self.frame_engines[0].size

    def do_many(self, name):
        def exec_func(*args, **kwargs):
            result = []
            for frame_engine in self.frame_engines:
                result.append(getattr(frame_engine, name)(*args, **kwargs))
            return result

        return exec_func


class BaseEngine:
    def __init__(self, context):
        self.context = context
        self.image = None
        self.extension = None
        self.source_width = None
        self.source_height = None
        self.icc_profile = None
        self.frame_count = 1
        self.metadata = None

    @classmethod
    def get_mimetype(cls, buffer):
        img_mime = None

        if buffer.startswith(b"GIF8"):
            img_mime = "image/gif"
        elif buffer.startswith(b"\x89PNG\r\n\x1a\n"):
            img_mime = "image/png"
        elif buffer.startswith(b"\xff\xd8"):
            img_mime = "image/jpeg"
        elif buffer.startswith(b"WEBP", 8):
            img_mime = "image/webp"
        elif buffer.startswith(b"\x00\x00\x00\x0c"):
            img_mime = "image/jp2"
        elif buffer[4:12] in (b"ftypavif", b"ftypavis"):
            img_mime = "image/avif"
        elif buffer[4:8] == b"ftyp" and buffer[8:12] in (
            b"heic",
            b"heix",
            b"heim",
            b"heis",
            b"mif1",
        ):
            img_mime = "image/heif"
        elif buffer.startswith(b"\x00\x00\x00 ftyp"):
            img_mime = "video/mp4"
        elif buffer.startswith(b"\x1aE\xdf\xa3"):
            img_mime = "video/webm"
        elif buffer.startswith((b"\x49\x49\x2a\x00", b"\x4d\x4d\x00\x2a")):
            img_mime = "image/tiff"
        elif SVG_RE.search(buffer[:2048].replace(b"\0", b"")):
            img_mime = "image/svg+xml"

        return img_mime

    def wrap(self, multiple_engine):
        for method_name in [
            "resize",
            "crop",
            "flip_vertically",
            "flip_horizontally",
        ]:
            setattr(self, method_name, multiple_engine.do_many(method_name))
        setattr(self, "read", multiple_engine.read)

    def is_multiple(self):
        return (
            hasattr(self, "multiple_engine")
            and self.multiple_engine is not None
        )

    def frame_engines(self):
        return self.multiple_engine.frame_engines

    def convert_svg_to_png(self, buffer):
        if not cairosvg:
            logger.error(
                "[BaseEngine] convert_svg_to_png failed: CairoSVG could not "
                "be loaded (%s)",
                CAIROSVG_IMPORT_ERROR
                or "install cairosvg to enable SVG conversion to PNG",
            )
            return buffer

        dpi = self.context.config.SVG_DPI
        try:
            tree = svg_parser.Tree(bytestring=buffer)
            output_width, output_height = self._svg_output_size(
                *svg_document_size(tree, dpi)
            )
            output = BytesIO()
            svg_surface.PNGSurface(
                tree,
                output,
                dpi,
                output_width=output_width,
                output_height=output_height,
            ).finish()
            buffer = output.getvalue()
            mime = self.get_mimetype(buffer)
            self.extension = EXTENSION.get(mime, ".jpg")
        except ParseError:
            mime = self.get_mimetype(buffer)
            extension = EXTENSION.get(mime)
            if extension is None or extension == ".svg":
                raise
            self.extension = extension

        return buffer

    def _svg_output_size(self, svg_width, svg_height):
        if svg_width <= 0 or svg_height <= 0:
            return self._svg_request_box()

        # The request describes the image being served, not auxiliary
        # images such as a watermark loaded through the same context.
        request = getattr(self.context, "request", None)
        is_request_image = request is not None and self is getattr(
            request, "engine", None
        )
        scale = 1
        if is_request_image:
            region_width, region_height = self._svg_crop_region(
                svg_width, svg_height
            )
            # orig is read from a raster after normalize() shrinks it past
            # the size limits, so it shrinks along with the document here.
            limit = min(1, self._limit_svg_scale(1, svg_width, svg_height))
            orig_size = (region_width * limit, region_height * limit)
            scale = self._svg_request_scale(
                region_width, region_height, orig_size
            )
        scale = self._limit_svg_scale(scale, svg_width, svg_height)
        if not self._svg_raster_fits(
            *_svg_raster_size(svg_width, svg_height, scale)
        ):
            return self._svg_request_box()
        if scale == 1:
            return None, None

        if is_request_image:
            self._scale_svg_request(scale, *orig_size)

        return svg_width * scale, None

    def _svg_raster_fits(self, width, height):
        config = self.context.config
        if max(width, height) > CAIRO_SIDE_LIMIT:
            return False
        if config.MAX_WIDTH and width > config.MAX_WIDTH:
            return False
        if config.MAX_HEIGHT and height > config.MAX_HEIGHT:
            return False
        max_pixels = _max_pixels(config)
        return not max_pixels or width * height <= max_pixels

    def _svg_request_box(self):
        request = getattr(self.context, "request", None)
        if request is None:
            return None, None
        width = _requested_pixels(request.width)
        height = _requested_pixels(request.height)
        if width and height:
            scale = self._limit_svg_scale(1, width, height)
            width, height = width * scale, height * scale
        return width, height

    def _svg_request_scale(self, region_width, region_height, orig_size):
        request = self.context.request
        target_width, target_height = self._svg_target_size(*orig_size)
        ratios = (target_width / region_width, target_height / region_height)
        fits_in = request.fit_in and not request.full
        scale = min(ratios) if fits_in else max(ratios)
        if self._no_upscale_requested():
            scale = min(scale, 1)

        return scale

    def _no_upscale_requested(self):
        filters = self.context.request.filters
        if not isinstance(filters, str):
            return False
        if not NO_UPSCALE_FILTER_RE.search(filters):
            return False
        factory = getattr(self.context, "filters_factory", None)
        return (
            factory is not None and "no_upscale" in factory.filter_classes_map
        )

    def _svg_crop_region(self, svg_width, svg_height):
        request = self.context.request
        if not request.should_crop:
            return svg_width, svg_height

        def limit(dimension, maximum):
            return min(max(dimension, 0), maximum)

        crop = request.crop
        left = limit(crop["left"], svg_width)
        top = limit(crop["top"], svg_height)
        right = limit(crop["right"], svg_width)
        bottom = limit(crop["bottom"], svg_height)
        if left >= right or top >= bottom:
            return svg_width, svg_height

        return right - left, bottom - top

    def _svg_target_size(self, source_width, source_height):
        request = self.context.request
        width = source_width if request.width == "orig" else request.width
        height = source_height if request.height == "orig" else request.height
        if not width and not height:
            return source_width, source_height
        if not width:
            width = source_width * height / source_height
        if not height:
            height = source_height * width / source_width

        if (
            request.fit_in
            and request.adaptive
            and _orientation_differs(
                source_width, source_height, width, height
            )
        ):
            width, height = height, width

        return width, height

    def _limit_svg_scale(self, scale, svg_width, svg_height):
        # The raster exists before normalize() and Pillow can shrink or
        # refuse it, and cairo refuses surfaces with a side above
        # CAIRO_SIDE_LIMIT, so the document is never drawn past any of them.
        config = self.context.config
        limits = [scale, CAIRO_SIDE_LIMIT / max(svg_width, svg_height)]
        if config.MAX_WIDTH:
            limits.append(config.MAX_WIDTH / svg_width)
        if config.MAX_HEIGHT:
            limits.append(config.MAX_HEIGHT / svg_height)
        max_pixels = _max_pixels(config)
        if max_pixels:
            limits.append(math.sqrt(max_pixels / (svg_width * svg_height)))
        scale = min(limits)
        # CairoSVG rounds each side, which can overshoot MAX_PIXELS.
        while (
            max_pixels
            and _svg_raster_pixels(svg_width, svg_height, scale) > max_pixels
        ):
            scale = (round(svg_width * scale) - 1) / svg_width

        # CairoSVG rejects a raster whose side rounds to zero pixels.
        return max(scale, 1 / min(svg_width, svg_height))

    def _scale_svg_request(self, scale, orig_width, orig_height):
        request = self.context.request
        if request.width == "orig":
            request.width = round(orig_width)
        if request.height == "orig":
            request.height = round(orig_height)
        for side in ("left", "top", "right", "bottom"):
            request.crop[side] = round(request.crop[side] * scale)
        for point in request.focal_points:
            point.x = round(point.x * scale)
            point.y = round(point.y * scale)
            point.width = round(point.width * scale)
            point.height = round(point.height * scale)
            point.weight = point.weight * scale * scale

    def load(self, buffer, extension):
        self.extension = extension

        if extension is None:
            mime = self.get_mimetype(buffer)
            self.extension = EXTENSION.get(mime, ".jpg")

        if self.extension == ".svg":
            buffer = self.convert_svg_to_png(buffer)

        image_or_frames = self.create_image(buffer)
        if image_or_frames is None:
            return

        try:
            if getattr(self, "exif", None):
                self.metadata = piexif.load(self.exif)
        except Exception as error:  # pylint: disable=broad-except
            logger.error("Error reading image metadata: %s", error)

        allow_animation = (
            self.context.config.ALLOW_ANIMATED_WEBP
            if self.extension == ".webp"
            else self.context.config.ALLOW_ANIMATED_GIFS
        )
        if allow_animation and isinstance(image_or_frames, (list, tuple)):
            self.image = image_or_frames[0]
            if len(image_or_frames) > 1:
                self.multiple_engine = MultipleEngine(self)
                for frame in image_or_frames:
                    self.multiple_engine.add_frame(frame)
                self.wrap(self.multiple_engine)
        else:
            self.image = image_or_frames

        if self.source_width is None:
            self.source_width = self.size[0]
        if self.source_height is None:
            self.source_height = self.size[1]

    @property
    def size(self):
        if self.is_multiple():
            return self.multiple_engine.size()
        return self.image.size

    def can_convert_to_webp(self):
        return (
            self.size[0] <= WEBP_SIDE_LIMIT and self.size[1] <= WEBP_SIDE_LIMIT
        )

    def normalize(self):
        width, height = self.size
        self.source_width = width
        self.source_height = height

        if (
            width > self.context.config.MAX_WIDTH
            or height > self.context.config.MAX_HEIGHT
        ):
            width_diff = width - self.context.config.MAX_WIDTH
            height_diff = height - self.context.config.MAX_HEIGHT
            if self.context.config.MAX_WIDTH and width_diff > height_diff:
                height = self.get_proportional_height(
                    self.context.config.MAX_WIDTH
                )
                self.resize(self.context.config.MAX_WIDTH, height)
                return True

            if self.context.config.MAX_HEIGHT and height_diff > width_diff:
                width = self.get_proportional_width(
                    self.context.config.MAX_HEIGHT
                )
                self.resize(width, self.context.config.MAX_HEIGHT)
                return True

        return False

    def get_proportional_width(self, new_height):
        width, height = self.size
        return round(float(new_height) * width / height, 0)

    def get_proportional_height(self, new_width):
        width, height = self.size
        return round(float(new_width) * height / width, 0)

    def _get_exif_object(self):
        if (not hasattr(self, "exif")) or self.exif is None:
            return None

        try:
            return ExifOrientationEditor(self.exif)
        except Exception as error:
            logger.exception("[exif] %s", error)

        return None

    def get_orientation(self):
        """
        Returns the image orientation of the buffer image or None
        if it is undefined. Gets the original value from the Exif tag.
        If the buffer has been rotated, then the value is adjusted to 1.
        :return: Orientation value (1 - 8)
        :rtype: int or None
        """
        exif = self._get_exif_object()

        return exif.get_orientation() if exif else None

    def reorientate(self, override_exif=True):
        """
        Rotates the image in the buffer so that it is oriented correctly.
        If override_exif is True (default) then the metadata
        orientation is adjusted as well.
        :param override_exif: If the metadata should be adjusted as well.
        :type override_exif: Boolean
        """
        exif = self._get_exif_object()
        if exif is None:
            return

        orientation = exif.get_orientation()

        if orientation is None:
            return

        if orientation == 2:
            self.flip_horizontally()
        elif orientation == 3:
            self.rotate(180)
        elif orientation == 4:
            self.flip_vertically()
        elif orientation == 5:
            # Horizontal Mirror + Rotation 270 CCW
            self.flip_vertically()
            self.rotate(270)
        elif orientation == 6:
            self.rotate(270)
        elif orientation == 7:
            # Vertical Mirror + Rotation 270 CCW
            self.flip_horizontally()
            self.rotate(270)
        elif orientation == 8:
            self.rotate(90)

        if orientation != 1 and override_exif:
            try:
                exif.set_orientation(1)
                self.exif = exif.tobytes()
            except Exception as error:
                logger.error("[exif] %s", error)

    def gen_image(self, size, color):
        raise NotImplementedError()

    def create_image(self, buffer):
        raise NotImplementedError()

    def crop(self, left, top, right, bottom):
        raise NotImplementedError()

    def resize(self, width, height):
        raise NotImplementedError()

    def focus(self, points):
        pass

    def flip_horizontally(self):
        raise NotImplementedError()

    def flip_vertically(self):
        raise NotImplementedError()

    def rotate(self, degrees):
        """
        Rotates the image the given amount CCW.
        :param degrees: Amount to rotate in degrees.
        :type amount: int
        """

    def read_multiple(self, images, extension=None):
        raise NotImplementedError()

    def read(self, extension, quality):
        raise NotImplementedError()

    def get_image_data(self):
        raise NotImplementedError()

    def set_image_data(self, data):
        raise NotImplementedError()

    def get_image_mode(self):
        """Possible return values should be: RGB, RBG, GRB, GBR,
        BRG, BGR, RGBA, AGBR, ..."""
        raise NotImplementedError()

    def paste(self, other_engine, pos, merge=True):
        raise NotImplementedError()

    def enable_alpha(self):
        raise NotImplementedError()

    def image_data_as_rgb(self, update_image=True):
        raise NotImplementedError()

    def strip_exif(self):
        pass

    def convert_to_grayscale(self, update_image=True, alpha=True):
        raise NotImplementedError()

    def draw_rectangle(
        self, x, y, width, height
    ):  # pylint: disable=invalid-name
        raise NotImplementedError()

    def strip_icc(self):
        pass

    def extract_cover(self):
        raise NotImplementedError()

    def has_transparency(self):
        raise NotImplementedError()

    def avif_enabled(self):
        raise NotImplementedError()

    def heif_enabled(self):
        raise NotImplementedError()

    def cleanup(self):
        pass

    def can_auto_convert_png_to_jpg(self):
        can_convert = self.extension == ".png" and not self.has_transparency()

        return can_convert

    def can_auto_convert_to_avif(self):
        return self.avif_enabled()

    def can_auto_convert_to_heif(self):
        return self.heif_enabled()
