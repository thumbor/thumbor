#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import os
from tempfile import mkstemp
from subprocess import Popen, PIPE
from io import BytesIO

from PIL import Image, ImageFile, ImageDraw, ImageSequence

from thumbor.engines import BaseEngine
from thumbor.engines.extensions.pil import GifWriter
from thumbor.utils import logger, deprecated

try:
    from thumbor.ext.filters import _composite
    FILTERS_AVAILABLE = True
except ImportError:
    FILTERS_AVAILABLE = False


FORMATS = {
    '.jpg': 'JPEG',
    '.jpeg': 'JPEG',
    '.gif': 'GIF',
    '.png': 'PNG',
    '.webp': 'WEBP'
}

ImageFile.MAXBLOCK = 2 ** 25

if hasattr(ImageFile, 'IGNORE_DECODING_ERRORS'):
    ImageFile.IGNORE_DECODING_ERRORS = True


class Engine(BaseEngine):

    def gen_image(self, size, color):
        if color == 'transparent':
            color = None
        img = Image.new("RGBA", size, color)
        return img

    def create_image(self, buffer):
        img = Image.open(BytesIO(buffer))
        self.icc_profile = img.info.get('icc_profile')
        self.transparency = img.info.get('transparency')
        self.exif = img.info.get('exif')

        if self.context.config.ALLOW_ANIMATED_GIFS and self.extension == '.gif':
            frames = []
            for frame in ImageSequence.Iterator(img):
                frames.append(frame.convert('P'))
            img.seek(0)
            return frames

        return img

    def draw_rectangle(self, x, y, width, height):
        # Nasty retry if the image is loaded for the first time and it's truncated
        try:
            d = ImageDraw.Draw(self.image)
        except IOError:
            d = ImageDraw.Draw(self.image)
        d.rectangle([x, y, x + width, y + height])

        del d

    def resize(self, width, height):
        if self.image.mode == 'P':
            logger.debug('converting image from 8-bit palette to 32-bit RGBA for resize')
            self.image = self.image.convert('RGBA')
        self.image = self.image.resize((int(width), int(height)), Image.ANTIALIAS)

    def crop(self, left, top, right, bottom):
        self.image = self.image.crop((
            int(left),
            int(top),
            int(right),
            int(bottom)
        ))

    def rotate(self, degrees):
        self.image = self.image.rotate(degrees)

    def flip_vertically(self):
        self.image = self.image.transpose(Image.FLIP_TOP_BOTTOM)

    def flip_horizontally(self):
        self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)

    def read(self, extension=None, quality=None):
        #returns image buffer in byte format.
        img_buffer = BytesIO()

        ext = extension or self.extension

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
                if self.image.format == 'JPEG':
                    quantization = getattr(self.image, 'quantization', None)
                    if quality is None and quantization and 2 <= len(quantization) <= 4:
                        options['quality'] = 'keep'

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
                    if self.image.mode != 'P':
                        mode = 'RGBA' if self.image.mode[-1] == 'A' else 'RGB'
                    self.image = self.image.convert(mode)

            if ext == '.png' and self.image.mode == 'CMYK':
                self.image = self.image.convert('RGBA')

            self.image.save(img_buffer, FORMATS[ext], **options)
        except IOError:
            logger.exception('Could not save as improved image, consider to increase ImageFile.MAXBLOCK')
            self.image.save(img_buffer, FORMATS[ext])
        except KeyError:
            logger.exception('Image format not found in PIL: %s' % ext)

            #extension is not present or could not help determine format => force JPEG
            if self.image.mode in ['P', 'RGBA', 'LA']:
                self.image.format = FORMATS['.png']
                self.image.save(img_buffer, FORMATS['.png'])
            else:
                self.image.format = FORMATS['.jpg']
                self.image.save(img_buffer, FORMATS['.jpg'])

        results = img_buffer.getvalue()
        img_buffer.close()
        return results

    def read_multiple(self, images, extension=None):
        gifWriter = GifWriter()
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

        images = gifWriter.convertImagesToPIL(converted_images, False, None)
        gifWriter.writeGifToFile(img_buffer, images, duration, loop, xy, dispose)

        results = img_buffer.getvalue()
        img_buffer.close()

        tmp_fd, tmp_file_path = mkstemp()
        f = os.fdopen(tmp_fd, "w")
        f.write(results)
        f.close()

        popen = Popen("gifsicle --colors 256 %s" % tmp_file_path, shell=True, stdout=PIPE)
        pipe = popen.stdout
        pipe_output = pipe.read()
        pipe.close()

        if popen.wait() == 0:
            results = pipe_output

        os.remove(tmp_file_path)

        return results

    @deprecated("Use image_data_as_rgb instead.")
    def get_image_data(self):
        return self.image.tostring()

    def set_image_data(self, data):
        self.image.fromstring(data)

    @deprecated("Use image_data_as_rgb instead.")
    def get_image_mode(self):
        return self.image.mode

    def image_data_as_rgb(self, update_image=True):
        converted_image = self.image
        if converted_image.mode not in ['RGB', 'RGBA']:
            if 'A' in converted_image.mode:
                converted_image = converted_image.convert('RGBA')
            else:
                converted_image = converted_image.convert('RGB')
        if update_image:
            self.image = converted_image
        return converted_image.mode, converted_image.tostring()

    def convert_to_grayscale(self):
        if 'A' in self.image.mode:
            self.image = self.image.convert('LA')
        else:
            self.image = self.image.convert('L')

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
