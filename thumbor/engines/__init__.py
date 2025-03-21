#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

# This is a base class, it makes sense to have many public methods and instance attributes
# pylint: disable=attribute-defined-outside-init,too-many-public-methods,unused-argument,too-many-instance-attributes,broad-except

import re
from xml.etree.ElementTree import ParseError
import piexif

from thumbor.engines.extensions.exif_orientation_editor import (
    ExifOrientationEditor,
)
from thumbor.utils import EXTENSION, logger

try:
    import cairosvg
except ImportError:
    cairosvg = None


WEBP_SIDE_LIMIT = 16383

SVG_RE = re.compile(
    b"<svg\s[^>]*([\"'])http[^\"']*svg[^\"']*",  # pylint: disable=anomalous-backslash-in-string
    re.I,
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
        elif buffer.startswith(b"\x49\x49\x2a\x00") or buffer.startswith(
            b"\x4d\x4d\x00\x2a"
        ):
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
            msg = """[BaseEngine] convert_svg_to_png failed cairosvg not
            imported (if you want svg conversion to png please install cairosvg)
            """
            logger.error(msg)
            return buffer

        try:
            buffer = cairosvg.svg2png(  # pylint: disable=no-member
                bytestring=buffer,
                dpi=self.context.config.SVG_DPI,
                output_width=self.context.request.width,
                output_height=self.context.request.height,
            )
            mime = self.get_mimetype(buffer)
            self.extension = EXTENSION.get(mime, ".jpg")
        except ParseError:
            mime = self.get_mimetype(buffer)
            extension = EXTENSION.get(mime)
            if extension is None or extension == ".svg":
                raise
            self.extension = extension

        return buffer

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

        if self.context.config.ALLOW_ANIMATED_GIFS and isinstance(
            image_or_frames, (list, tuple)
        ):
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
