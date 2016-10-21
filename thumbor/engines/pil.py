#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import warnings
import os
from tempfile import mkstemp
from subprocess import Popen, PIPE
from io import BytesIO

from PIL import Image, ImageFile, ImageDraw, ImageSequence, JpegImagePlugin

try:
    from cv2 import cv
except:
    cv = None

from thumbor.engines import BaseEngine
from thumbor.engines.extensions.pil import GifWriter
from thumbor.utils import logger, deprecated, EXTENSION

try:
    from thumbor.ext.filters import _composite
    FILTERS_AVAILABLE = True
except ImportError:
    FILTERS_AVAILABLE = False


FORMATS = {
    '.tif': 'PNG',  # serve tif as png
    '.jpg': 'JPEG',
    '.jpeg': 'JPEG',
    '.gif': 'GIF',
    '.png': 'PNG',
    '.webp': 'WEBP'
}

ImageFile.MAXBLOCK = 2 ** 25
ImageFile.LOAD_TRUNCATED_IMAGES = True

if hasattr(ImageFile, 'IGNORE_DECODING_ERRORS'):
    ImageFile.IGNORE_DECODING_ERRORS = True


class Engine(BaseEngine):
    def __init__(self, context):
        super(Engine, self).__init__(context)
        self.subsampling = None
        self.qtables = None

        if self.context and self.context.config.MAX_PIXELS:
            Image.MAX_IMAGE_PIXELS = self.context.config.MAX_PIXELS
        # Error on Image.open when image pixel count is above MAX_IMAGE_PIXELS
        warnings.simplefilter('error', Image.DecompressionBombWarning)

    def gen_image(self, size, color):
        if color == 'transparent':
            color = None
        img = Image.new("RGBA", size, color)
        return img

    def create_image(self, buffer):
        try:
            img = Image.open(BytesIO(buffer))
        except Image.DecompressionBombWarning as e:
            logger.warning("[PILEngine] create_image failed: {0}".format(e))
            return None
        self.icc_profile = img.info.get('icc_profile')
        self.transparency = img.info.get('transparency')
        self.exif = img.info.get('exif')

        self.subsampling = JpegImagePlugin.get_sampling(img)
        if (self.subsampling == -1):  # n/a for this file
            self.subsampling = None
        self.qtables = getattr(img, 'quantization', None)

        if self.context.config.ALLOW_ANIMATED_GIFS and self.extension == '.gif':
            frames = []
            for frame in ImageSequence.Iterator(img):
                frames.append(frame.convert('P'))
            img.seek(0)
            self.frame_count = len(frames)
            return frames

        return img

    def get_resize_filter(self):
        config = self.context.config
        resample = config.PILLOW_RESAMPLING_FILTER if config.PILLOW_RESAMPLING_FILTER is not None else 'LANCZOS'

        available = {
            'LANCZOS': Image.LANCZOS,
            'NEAREST': Image.NEAREST,
            'BILINEAR': Image.BILINEAR,
            'BICUBIC': Image.BICUBIC,
        }

        if hasattr(Image, 'HAMMING'):
            available['HAMMING'] = Image.HAMMING

        return available.get(resample.upper(), Image.LANCZOS)

    def draw_rectangle(self, x, y, width, height):
        # Nasty retry if the image is loaded for the first time and it's truncated
        try:
            d = ImageDraw.Draw(self.image)
        except IOError:
            d = ImageDraw.Draw(self.image)
        d.rectangle([x, y, x + width, y + height])

        del d

    def resize(self, width, height):
        mode = self.image.mode
        if self.image.mode == 'P':
            logger.debug('converting image from 8-bit palette to 32-bit RGBA for resize')
            mode = 'RGBA'

        resample = self.get_resize_filter()

        self.image.draft(mode, (int(width), int(height)))
        self.image = self.image.resize((int(width), int(height)), resample)

    def crop(self, left, top, right, bottom):
        self.image = self.image.crop((
            int(left),
            int(top),
            int(right),
            int(bottom)
        ))

    def rotate(self, degrees):
        # PIL rotates counter clockwise
        if degrees == 90:
            self.image = self.image.transpose(Image.ROTATE_90)
        elif degrees == 180:
            self.image = self.image.transpose(Image.ROTATE_180)
        elif degrees == 270:
            self.image = self.image.transpose(Image.ROTATE_270)
        else:
            self.image = self.image.rotate(degrees, expand=1)

    def flip_vertically(self):
        self.image = self.image.transpose(Image.FLIP_TOP_BOTTOM)

    def flip_horizontally(self):
        self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)

    def get_default_extension(self):
        # extension is not present => force JPEG or PNG
        if self.image.mode in ['P', 'RGBA', 'LA']:
            return '.png'
        else:
            return '.jpeg'

    def read(self, extension=None, quality=None):  # NOQA
        # returns image buffer in byte format.
        img_buffer = BytesIO()
        ext = extension or self.extension or self.get_default_extension()

        options = {
            'quality': quality
        }
        if ext == '.jpg' or ext == '.jpeg':
            options['optimize'] = True
            if self.context.config.PROGRESSIVE_JPEG:
                # Can't simply set options['progressive'] to the value
                # of self.context.config.PROGRESSIVE_JPEG because save
                # operates on the presence of the key in **options, not
                # the value of that setting.
                options['progressive'] = True

            if self.image.mode != 'RGB':
                self.image = self.image.convert('RGB')
            else:
                subsampling_config = self.context.config.PILLOW_JPEG_SUBSAMPLING
                qtables_config = self.context.config.PILLOW_JPEG_QTABLES

                if subsampling_config is not None or qtables_config is not None:
                    options['quality'] = 0  # can't use 'keep' here as Pillow would try to extract qtables/subsampling and fail
                    orig_subsampling = self.subsampling
                    orig_qtables = self.qtables

                    if (subsampling_config == 'keep' or subsampling_config is None) and (orig_subsampling is not None):
                        options['subsampling'] = orig_subsampling
                    else:
                        options['subsampling'] = subsampling_config

                    if (qtables_config == 'keep' or qtables_config is None) and (orig_qtables and 2 <= len(orig_qtables) <= 4):
                        options['qtables'] = orig_qtables
                    else:
                        options['qtables'] = qtables_config

        if options['quality'] is None:
            options['quality'] = self.context.config.QUALITY

        if self.icc_profile is not None:
            options['icc_profile'] = self.icc_profile

        if self.context.config.PRESERVE_EXIF_INFO:
            if self.exif is not None:
                options['exif'] = self.exif

        if self.image.mode == 'P' and self.transparency:
            options['transparency'] = self.transparency

        try:
            if ext == '.webp':
                if self.image.mode not in ['RGB', 'RGBA']:
                    mode = None
                    if self.image.mode == 'P':
                        mode = 'RGBA'
                    else:
                        mode = 'RGBA' if self.image.mode[-1] == 'A' else 'RGB'
                    self.image = self.image.convert(mode)

            if ext in ['.png', '.gif'] and self.image.mode == 'CMYK':
                self.image = self.image.convert('RGBA')
            self.image.format = FORMATS.get(ext, FORMATS[self.get_default_extension()])
            self.image.save(img_buffer, self.image.format, **options)
        except IOError:
            logger.exception('Could not save as improved image, consider to increase ImageFile.MAXBLOCK')
            self.image.save(img_buffer, FORMATS[ext])

        results = img_buffer.getvalue()
        img_buffer.close()
        self.extension = ext
        return results

    def read_multiple(self, images, extension=None):
        gif_writer = GifWriter()
        img_buffer = BytesIO()

        duration = []
        converted_images = []
        xy = []
        dispose = []

        for im in images:
            duration.append(float(im.info.get('duration', 80)) / 1000)
            converted_images.append(im.convert("RGB"))
            xy.append((0, 0))
            dispose.append(1)

        loop = int(self.image.info.get('loop', 1))

        images = gif_writer.convertImagesToPIL(converted_images, False, None)
        gif_writer.writeGifToFile(img_buffer, images, duration, loop, xy, dispose)

        results = img_buffer.getvalue()
        img_buffer.close()

        tmp_fd, tmp_file_path = mkstemp()
        f = os.fdopen(tmp_fd, "w")
        f.write(results)
        f.close()

        command = [
            'gifsicle',
            '--colors',
            '256',
            tmp_file_path
        ]

        popen = Popen(command, stdout=PIPE)
        pipe = popen.stdout
        pipe_output = pipe.read()
        pipe.close()

        if popen.wait() == 0:
            results = pipe_output

        os.remove(tmp_file_path)

        return results

    def convert_tif_to_png(self, buffer):
        if not cv:
            msg = """[PILEngine] convert_tif_to_png failed: opencv not imported"""
            logger.error(msg)
            return buffer

        # can not use cv2 here, because ubuntu precise shipped with python-opencv 2.3 which has bug with imencode
        # requires 3rd parameter buf which could not be created in python. Could be replaced with these lines:
        # img = cv2.imdecode(numpy.fromstring(buffer, dtype='uint16'), -1)
        # buffer = cv2.imencode('.png', img)[1].tostring()
        mat_data = cv.CreateMatHeader(1, len(buffer), cv.CV_8UC1)
        cv.SetData(mat_data, buffer, len(buffer))
        img = cv.DecodeImage(mat_data, -1)
        buffer = cv.EncodeImage(".png", img).tostring()

        mime = self.get_mimetype(buffer)
        self.extension = EXTENSION.get(mime, '.jpg')
        return buffer

    def load(self, buffer, extension):
        self.extension = extension

        if extension is None:
            mime = self.get_mimetype(buffer)
            self.extension = EXTENSION.get(mime, '.jpg')

        if self.extension == '.tif':  # Pillow does not support 16bit per channel TIFF images
            buffer = self.convert_tif_to_png(buffer)

        super(Engine, self).load(buffer, self.extension)

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
        if converted_image.mode not in ['RGB', 'RGBA', 'P']:
            if 'A' in converted_image.mode:
                converted_image = converted_image.convert('RGBA')
            else:
                converted_image = converted_image.convert('RGB')
        if update_image:
            self.image = converted_image
        return converted_image.mode, converted_image.tobytes()

    def convert_to_grayscale(self, update_image=True, with_alpha=True):
        if 'A' in self.image.mode and with_alpha:
            image = self.image.convert('LA')
        else:
            image = self.image.convert('L')
        if update_image:
            self.image = image
        return image

    def paste(self, other_engine, pos, merge=True):
        if merge and not FILTERS_AVAILABLE:
            raise RuntimeError(
                'You need filters enabled to use paste with merge. Please reinstall ' +
                'thumbor with proper compilation of its filters.')

        self.enable_alpha()
        other_engine.enable_alpha()

        image = self.image
        other_image = other_engine.image

        if merge:
            sz = self.size
            other_size = other_engine.size
            mode, data = self.image_data_as_rgb()
            other_mode, other_data = other_engine.image_data_as_rgb()
            imgdata = _composite.apply(
                mode, data, sz[0], sz[1],
                other_data, other_size[0], other_size[1], pos[0], pos[1])
            self.set_image_data(imgdata)
        else:
            image.paste(other_image, pos)

    def enable_alpha(self):
        if self.image.mode != 'RGBA':
            self.image = self.image.convert('RGBA')

    def strip_icc(self):
        self.icc_profile = None
