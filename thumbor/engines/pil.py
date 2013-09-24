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

from PIL.ExifTags import TAGS
from PIL import Image, ImageFile, ImageDraw, ImageSequence

from thumbor.engines import BaseEngine
from thumbor.engines.extensions.pil import GifWriter
from thumbor.utils import logger

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
        img = Image.new("RGBA", size, color)
        return img

    def create_image(self, buffer):
        img = Image.open(BytesIO(buffer))
        self.icc_profile = img.info.get('icc_profile', None)

        if self.context.config.ALLOW_ANIMATED_GIFS and self.extension == '.gif':
            frames = []
            for frame in ImageSequence.Iterator(img):
                frames.append(frame.convert())
            img.seek(0)
            return frames

        return img

    def draw_rectangle(self, x, y, width, height):
        d = ImageDraw.Draw(self.image)
        d.rectangle([x, y, x + width, y + height])

        del d

    @property
    def exif(self):
        """Get embedded EXIF data from image file."""
        ret = {}
        if hasattr(self.image, '_getexif'):
            exifinfo = self.image._getexif()
            if exifinfo is not None:
                for tag, value in exifinfo.items():
                    decoded = TAGS.get(tag, tag)
                    ret[decoded] = value
        return ret

    def resize(self, width, height):
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
        if quality is None:
            quality = self.context.request.quality
        #returns image buffer in byte format.
        img_buffer = BytesIO()

        ext = extension or self.extension
        options = {
            'quality': quality
        }
        if ext == '.jpg' or ext == '.jpeg':
            options['optimize'] = True
            options['progressive'] = True

        if self.icc_profile is not None:
            options['icc_profile'] = self.icc_profile

        if self.context.config.PRESERVE_EXIF_INFO:
            exif = self.image.info.get('exif', None)
            if exif is not None:
                options['exif'] = exif

        try:
            if ext == '.webp':
                if self.image.mode not in ['RGB', 'RGBA']:
                    self.image = self.image.convert()

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

    def get_image_data(self, image=None):
        if image is None:
            return self.image.tostring()
        else:
            return image.tostring()

    def set_image_data(self, data):
        self.image.fromstring(data)

    def get_image_mode(self):
        return self.image.mode

    def convert_to_rgb(self):
        converted_image = self.image.convert('RGB')
        return converted_image.mode, self.get_image_data(converted_image)

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
            imgdata = _composite.apply(
                self.get_image_mode(), self.get_image_data(), sz[0], sz[1],
                other_engine.get_image_data(), other_size[0], other_size[1], pos[0], pos[1])
            self.set_image_data(imgdata)
        else:
            image.paste(other_image, pos)

    def enable_alpha(self):
        if self.image.mode != 'RGBA':
            self.image = self.image.convert('RGBA')

    def strip_icc(self):
        self.icc_profile = None
