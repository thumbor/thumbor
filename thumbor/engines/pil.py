#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from io import BytesIO

import piexif
from JpegIPTC import JpegIPTC
from PIL import Image, ImageDraw, ImageFile, ImageSequence, JpegImagePlugin
from PIL import features as pillow_features

from thumbor.engines import BaseEngine
from thumbor.filters.fill import Filter
from thumbor.utils import deprecated, ensure_srgb, get_color_space, logger

try:
    from thumbor.ext.filters import _composite

    FILTERS_AVAILABLE = True
except ImportError:
    FILTERS_AVAILABLE = False

try:
    from PIL import _avif  # pylint: disable=ungrouped-imports
except ImportError:
    try:
        from pillow_avif import _avif
    except ImportError:
        _avif = None

try:
    from pillow_heif import HeifImagePlugin
except ImportError:
    HeifImagePlugin = None

HAVE_AVIF = _avif is not None
HAVE_HEIF = HeifImagePlugin is not None


FORMATS = {
    ".tif": "PNG",  # serve tif as png
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".gif": "GIF",
    ".png": "PNG",
    ".webp": "WEBP",
    ".avif": "AVIF",
    ".heic": "HEIF",
    ".heif": "HEIF",
}

KEEP_EXIF_COPYRIGHT_TAGS = [
    piexif.ImageIFD.Artist,
    piexif.ImageIFD.Copyright,
    piexif.ImageIFD.DateTime,
]

ImageFile.MAXBLOCK = 2**25
ImageFile.LOAD_TRUNCATED_IMAGES = True

DECOMPRESSION_BOMB_EXCEPTIONS = (Image.DecompressionBombWarning,)

if hasattr(Image, "DecompressionBombError"):
    DECOMPRESSION_BOMB_EXCEPTIONS += (Image.DecompressionBombError,)


class Engine(BaseEngine):
    def __init__(self, context):
        super().__init__(context)
        self.subsampling = None
        self.qtables = None
        self.original_mode = None
        self.exif = None
        self.iptc = None

        try:
            if self.context.config.MAX_PIXELS is None or int(
                self.context.config.MAX_PIXELS
            ):
                Image.MAX_IMAGE_PIXELS = self.context.config.MAX_PIXELS
        except (AttributeError, TypeError, ValueError):  # invalid type
            logger.info(
                "MAX_PIXELS config variable set to invalid type. Has to be int on None"
            )

    def gen_image(self, size, color):
        if color == "transparent":
            color = None
        elif color == "auto":
            color = Filter.get_median_color(self.context.modules)
            color = f"#{color}"

        img = Image.new("RGBA", size, color)

        return img

    def create_image(self, buffer):
        try:
            img = Image.open(BytesIO(buffer))
        except DECOMPRESSION_BOMB_EXCEPTIONS as error:
            logger.warning("[PILEngine] create_image failed: %s", error)

            return None
        self.icc_profile = img.info.get("icc_profile")
        self.exif = img.info.get("exif")
        self.original_mode = img.mode

        if self.context.config.PRESERVE_IPTC_INFO:
            jpegiptc_object = JpegIPTC()
            jpegiptc_object.load_from_binarydata(buffer)
            self.iptc = jpegiptc_object.get_raw_iptc()

        if hasattr(img, "layer"):
            self.subsampling = JpegImagePlugin.get_sampling(img)
            if self.subsampling == -1:  # n/a for this file
                self.subsampling = None

        self.qtables = getattr(img, "quantization", None)

        if (
            self.context.config.ALLOW_ANIMATED_GIFS
            and self.extension == ".gif"
        ):
            frames = []

            for frame in ImageSequence.Iterator(img):
                frames.append(frame.convert("P"))
            img.seek(0)
            self.frame_count = len(frames)

            return frames

        return img

    def get_exif_copyright(self):
        try:
            exifs = piexif.load(self.image.info.get("exif"))
        except Exception:
            return self.image.info.get("exif")

        return self.extract_copyright_from_exif(exifs)

    def extract_copyright_from_exif(self, exifs):
        copyright_exif = {}

        if exifs is None or "0th" not in exifs or exifs["0th"] is None:
            return None

        for copyright_tag in KEEP_EXIF_COPYRIGHT_TAGS:
            if copyright_tag in exifs["0th"]:
                copyright_exif[copyright_tag] = exifs["0th"][copyright_tag]

        return piexif.dump({"0th": copyright_exif})

    def get_resize_filter(self):
        config = self.context.config
        resample = (
            config.PILLOW_RESAMPLING_FILTER
            if config.PILLOW_RESAMPLING_FILTER is not None
            else "LANCZOS"
        )

        available = {
            "LANCZOS": Image.Resampling.LANCZOS,
            "NEAREST": Image.Resampling.NEAREST,
            "BILINEAR": Image.Resampling.BILINEAR,
            "BICUBIC": Image.Resampling.BICUBIC,
            "HAMMING": Image.Resampling.HAMMING,
        }

        return available.get(resample.upper(), Image.Resampling.LANCZOS)

    def draw_rectangle(self, x, y, width, height):
        # Nasty retry if the image is loaded for the first time and it's truncated
        try:
            draw_image = ImageDraw.Draw(self.image)
        except IOError:
            draw_image = ImageDraw.Draw(self.image)
        draw_image.rectangle([x, y, x + width, y + height])

        del draw_image

    def resize(self, width, height):
        # Indexed color modes (such as 1 and P) will be forced to use a
        # nearest neighbor resampling algorithm. So we convert them to
        # RGB(A) mode before resizing to avoid nasty scaling artifacts.

        if self.image.mode in ["1", "P"]:
            logger.debug(
                "converting image from 8-bit/1-bit palette to 32-bit RGB(A) for resize"
            )

            if self.image.mode == "1":
                target_mode = "RGB"
            else:
                # convert() figures out RGB or RGBA based on palette used
                target_mode = None
            self.image = self.image.convert(mode=target_mode)

        size = (int(width), int(height))
        # Tell image loader what target size we want (only JPG for a moment)
        self.image.draft(None, size)

        resample = self.get_resize_filter()
        self.image = self.image.resize(size, resample)

    def crop(self, left, top, right, bottom):
        self.image = self.image.crop(
            (int(left), int(top), int(right), int(bottom))
        )

    def rotate(self, degrees):
        # PIL rotates counter clockwise

        if degrees == 90:
            self.image = self.image.transpose(Image.Transpose.ROTATE_90)
        elif degrees == 180:
            self.image = self.image.transpose(Image.Transpose.ROTATE_180)
        elif degrees == 270:
            self.image = self.image.transpose(Image.Transpose.ROTATE_270)
        else:
            self.image = self.image.rotate(degrees, expand=1)

    def flip_vertically(self):
        self.image = self.image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

    def flip_horizontally(self):
        self.image = self.image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

    def get_default_extension(self):
        # extension is not present => force JPEG or PNG

        if self.image.mode in ["P", "RGBA", "LA"]:
            return ".png"

        return ".jpeg"

    # TODO: Refactor this
    def read(  # noqa
        self, extension=None, quality=None
    ):  # noqa pylint: disable=too-many-statements,too-many-branches
        # returns image buffer in byte format.

        img_buffer = BytesIO()
        requested_extension = extension or self.extension

        # 1 and P mode images will be much smaller if converted back to
        # their original mode. So let's do that after resizing. Get $$.

        if (
            self.context.config.PILLOW_PRESERVE_INDEXED_MODE
            and requested_extension in [None, ".png", ".gif"]
            and self.original_mode in ["P", "1"]
            and self.original_mode != self.image.mode
        ):
            if self.original_mode == "1":
                self.image = self.image.convert("1")
            else:
                # libimagequant might not be enabled on compile time
                # but it's better than default octree for RGBA images
                quantize_method = (
                    Image.Quantize.LIBIMAGEQUANT
                    if pillow_features.check("libimagequant")
                    else None
                )
                self.image = self.image.quantize(method=quantize_method)

        ext = requested_extension or self.get_default_extension()

        if ext in (".heic", ".heif") and not HAVE_HEIF:
            logger.warning(
                "[PILEngine] HEIF encoding unavailable, defaulting to %s",
                self.extension,
            )
            ext = self.extension

        if ext == ".avif" and not HAVE_AVIF:
            logger.warning(
                "[PILEngine] AVIF encoding unavailable, defaulting to %s",
                self.extension,
            )
            ext = self.extension

        options = {"quality": quality}

        if ext in (".jpg", ".jpeg"):
            options["optimize"] = True

            if self.context.config.PROGRESSIVE_JPEG:
                # Can't simply set options['progressive'] to the value
                # of self.context.config.PROGRESSIVE_JPEG because save
                # operates on the presence of the key in **options, not
                # the value of that setting.
                options["progressive"] = True

            if self.image.mode != "RGB":
                self.image = self.image.convert("RGB")
            else:
                subsampling_config = (
                    self.context.config.PILLOW_JPEG_SUBSAMPLING
                )
                qtables_config = self.context.config.PILLOW_JPEG_QTABLES

                if (
                    subsampling_config is not None
                    or qtables_config is not None
                ):
                    # can't use 'keep' here as Pillow would try to extract
                    # qtables/subsampling and fail
                    options["quality"] = 0

                    orig_subsampling = self.subsampling
                    orig_qtables = self.qtables

                    if (
                        subsampling_config == "keep"
                        or subsampling_config is None
                    ) and (orig_subsampling is not None):
                        options["subsampling"] = orig_subsampling
                    else:
                        options["subsampling"] = subsampling_config

                    if (
                        qtables_config == "keep" or qtables_config is None
                    ) and (orig_qtables and 2 <= len(orig_qtables) <= 4):
                        options["qtables"] = orig_qtables
                    else:
                        options["qtables"] = qtables_config

        if (
            ext == ".png"
            and self.context.config.PNG_COMPRESSION_LEVEL is not None
        ):
            options["compress_level"] = (
                self.context.config.PNG_COMPRESSION_LEVEL
            )

        if options["quality"] is None:
            options["quality"] = self.context.config.QUALITY

        if ext == ".avif":
            options["codec"] = self.context.config.AVIF_CODEC
            if self.context.config.AVIF_SPEED:
                options["speed"] = self.context.config.AVIF_SPEED

            if options["codec"] == "svt":
                width, height = self.size
                # SVT-AV1 has limits on min and max image dimension. If the
                # image falls outside of those, use AVIF_CODEC_FALLBACK
                if not 64 <= width <= 4096 or not 64 <= height <= 4096:
                    options["codec"] = self.context.config.AVIF_CODEC_FALLBACK
                elif width % 2 or height % 2:
                    # SVT-AV1 requires width and height to be divisible by two
                    width = (width // 2) * 2
                    height = (height // 2) * 2
                    self.crop(0, 0, width, height)

            if options["quality"] == "keep":
                options.pop("quality")

            if self.image.mode not in ["RGB", "RGBA"]:
                if self.image.mode == "P":
                    mode = "RGBA"
                else:
                    mode = "RGBA" if self.image.mode[-1] == "A" else "RGB"
                self.image = self.image.convert(mode)

            # Some AVIF decoders (most notably the one in Chrome) do not
            # display AVIF images if they have an embedded ICC profile with a
            # color space that doesn't match the image's mode (e.g. if the
            # mode is RGB but the profile is CMYK or GRAY).
            #
            # To address this issue we transform non-sRGB ICC profiles to sRGB
            # if we're encoding to AVIF.
            color_space = get_color_space(self.image)
            if color_space not in ("RGB", None):
                srgb_image = ensure_srgb(
                    self.image, srgb_profile=self.context.config.SRGB_PROFILE
                )
                if srgb_image:
                    self.image = srgb_image
                    self.icc_profile = srgb_image.info.get("icc_profile")

        if self.icc_profile is not None:
            options["icc_profile"] = self.icc_profile

        if (
            self.context.config.PRESERVE_EXIF_COPYRIGHT_INFO is True
            and self.image.info.get("exif") is not None
        ):
            exif_copyright = self.get_exif_copyright()
            if exif_copyright is not None:
                options["exif"] = exif_copyright

        if self.context.config.PRESERVE_EXIF_INFO:
            if self.exif is not None:
                options["exif"] = self.exif

        try:
            if ext == ".webp":
                if options["quality"] == 100:
                    logger.debug("webp quality is 100, using lossless instead")
                    options["lossless"] = True
                    options.pop("quality")

                if self.image.mode not in ["RGB", "RGBA"]:
                    if self.image.mode == "P":
                        mode = "RGBA"
                    else:
                        mode = "RGBA" if self.image.mode[-1] == "A" else "RGB"
                    self.image = self.image.convert(mode)

            if (
                ext in [".png", ".gif", ".heic", ".heif"]
                and self.image.mode == "CMYK"
            ):
                # 26.10.22: remove ".heic, .heif" in a month(when pillow_heif get updated)
                self.image = self.image.convert("RGBA")

            self.image.format = FORMATS.get(
                ext, FORMATS[self.get_default_extension()]
            )
            self.image.save(img_buffer, self.image.format, **options)
        except IOError:
            logger.exception(
                "Could not save as improved image, consider to increase ImageFile.MAXBLOCK"
            )
            self.image.save(img_buffer, FORMATS[ext])

        results = img_buffer.getvalue()
        img_buffer.close()
        self.extension = ext

        if self.context.config.PRESERVE_IPTC_INFO:
            jpegiptc_object_d = JpegIPTC()
            jpegiptc_object_d.load_from_binarydata(results)
            jpegiptc_object_d.set_raw_iptc(self.iptc)
            newresults = jpegiptc_object_d.dump()
            if newresults is not None:
                results = newresults

        return results

    def read_multiple(self, images, extension=None):
        self.image.format = FORMATS.get(
            extension or self.extension, FORMATS[self.get_default_extension()]
        )
        with BytesIO() as img_buffer:
            images[0].save(
                img_buffer,
                self.image.format,
                save_all=True,
                append_images=images[1:],
                duration=[im.info.get("duration", 80) / 1000 for im in images],
                loop=int(self.image.info.get("loop", 1)),
            )
            return img_buffer.getvalue()

    @deprecated("Use image_data_as_rgb instead.")
    def get_image_data(self):
        return self.image.tobytes()

    def set_image_data(self, data):
        self.image.frombytes(data)

    @deprecated("Use image_data_as_rgb instead.")
    def get_image_mode(self):
        return self.image.mode

    def image_data_as_rgb(self, update_image=True):
        converted_image = self.image

        if converted_image.mode not in ["RGB", "RGBA"]:
            if "A" in converted_image.mode:
                converted_image = converted_image.convert("RGBA")
            elif converted_image.mode == "P":
                # convert() figures out RGB or RGBA based on palette used
                converted_image = converted_image.convert(None)
            else:
                converted_image = converted_image.convert("RGB")

        if update_image:
            self.image = converted_image

        return converted_image.mode, converted_image.tobytes()

    def convert_to_grayscale(self, update_image=True, alpha=True):
        if "A" in self.image.mode and alpha:
            image = self.image.convert("LA")
        else:
            image = self.image.convert("L")

        if update_image:
            self.image = image

        return image

    def has_transparency(self):
        has_transparency = (
            "A" in self.image.mode or "transparency" in self.image.info
        )

        if has_transparency:
            # If the image has alpha channel,
            # we check for any pixels that are not opaque (255)
            has_transparency = (
                min(self.image.convert("RGBA").getchannel("A").getextrema())
                < 255
            )

        return has_transparency

    def avif_enabled(self):
        return HAVE_AVIF

    def heif_enabled(self):
        return HAVE_HEIF

    def paste(self, other_engine, pos, merge=True):
        if merge and not FILTERS_AVAILABLE:
            raise RuntimeError(
                "You need filters enabled to use paste with merge. Please reinstall "
                + "thumbor with proper compilation of its filters."
            )

        self.enable_alpha()
        other_engine.enable_alpha()

        image = self.image
        other_image = other_engine.image

        if merge:
            image_size = self.size
            other_size = other_engine.size
            mode, data = self.image_data_as_rgb()
            _, other_data = other_engine.image_data_as_rgb()
            imgdata = _composite.apply(
                mode,
                data,
                image_size[0],
                image_size[1],
                other_data,
                other_size[0],
                other_size[1],
                int(pos[0]),
                int(pos[1]),
            )
            self.set_image_data(imgdata)
        else:
            image.paste(other_image, pos)

    def enable_alpha(self):
        if self.image.mode != "RGBA":
            self.image = self.image.convert("RGBA")

    def strip_icc(self):
        self.icc_profile = None

    def strip_exif(self):
        self.exif = None
