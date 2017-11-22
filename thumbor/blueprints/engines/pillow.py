#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

'''
Engine responsible for image operations using pillow.
'''

from io import BytesIO

import tornado.gen
from PIL import Image

from thumbor.lifecycle import Events

FORMATS = {
    'image/tif': 'PNG',  # serve tif as png
    'image/jpg': 'JPEG',
    'image/jpeg': 'JPEG',
    'image/gif': 'GIF',
    'image/png': 'PNG',
    'image/webp': 'WEBP'
}


def plug_into_lifecycle():
    Events.subscribe(Events.Imaging.before_transforming_image, on_before_transforming_image)
    Events.subscribe(Events.Imaging.image_transforming_phase_1, on_image_transforming_phase_1)
    Events.subscribe(Events.Imaging.after_transforming_image, on_after_transforming_image)


@tornado.gen.coroutine
def on_before_transforming_image(sender, request, details):
    try:
        details.metadata['image'] = Image.open(BytesIO(details.source_image))
    except Image.DecompressionBombWarning as e:
        details.finish_early = True
        details.body = 'Image could not be loaded by PIL engine'
        details.status_code = 500
        return False

        # self.icc_profile = img.info.get('icc_profile')
        # self.transparency = img.info.get('transparency')
        # self.exif = img.info.get('exif')

        # self.subsampling = JpegImagePlugin.get_sampling(img)
        # if (self.subsampling == -1):  # n/a for this file
            # self.subsampling = None
        # self.qtables = getattr(img, 'quantization', None)

        # if self.context.config.ALLOW_ANIMATED_GIFS and self.extension == '.gif':
            # frames = []
            # for frame in ImageSequence.Iterator(img):
                # frames.append(frame.convert('P'))
            # img.seek(0)
            # self.frame_count = len(frames)
            # return frames

        # return img


@tornado.gen.coroutine
def on_image_transforming_phase_1(sender, request, details):
    req = details.request_parameters
    if req.should_crop:
        crop(details, req.crop['left'], req.crop['top'], req.crop['right'], req.crop['bottom'])
    resize(details, req.width, req.height)


def crop(details, left, top, right, bottom):
    img = details.metadata['image']
    img = img.crop((
        int(left),
        int(top),
        int(right),
        int(bottom)
    ))
    details.metadata['image'] = img


def get_resize_filter(details):
    config = details.config
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


def resize(details, width, height):
    img = details.metadata['image']

    # Indexed color modes (such as 1 and P) will be forced to use a
    # nearest neighbor resampling algorithm. So we convert them to
    # RGBA mode before resizing to avoid nasty scaling artifacts.
    original_mode = img.mode
    if img.mode in ['1', 'P']:
        # logger.debug('converting image from 8-bit/1-bit palette to 32-bit RGBA for resize')
        img = img.convert('RGBA')

    resample = get_resize_filter(details)
    img = img.resize((int(width), int(height)), resample)

    # 1 and P mode images will be much smaller if converted back to
    # their original mode. So let's do that after resizing. Get $$.
    if original_mode != img.mode:
        img = img.convert(original_mode)

    details.metadata['image'] = img


@tornado.gen.coroutine
def on_after_transforming_image(sender, request, details):
    serialize_image(details)


def serialize_image(details):
    # returns image buffer in byte format.
    img_buffer = BytesIO()

    options = {
        'quality': details.config.QUALITY,
    }
    # if ext == '.jpg' or ext == '.jpeg':
        # options['optimize'] = True
        # if self.context.config.PROGRESSIVE_JPEG:
            # # Can't simply set options['progressive'] to the value
            # # of self.context.config.PROGRESSIVE_JPEG because save
            # # operates on the presence of the key in **options, not
            # # the value of that setting.
            # options['progressive'] = True

        # if self.image.mode != 'RGB':
            # self.image = self.image.convert('RGB')
        # else:
            # subsampling_config = self.context.config.PILLOW_JPEG_SUBSAMPLING
            # qtables_config = self.context.config.PILLOW_JPEG_QTABLES

            # if subsampling_config is not None or qtables_config is not None:
                # options['quality'] = 0  # can't use 'keep' here as Pillow would try to extract qtables/subsampling and fail
                # orig_subsampling = self.subsampling
                # orig_qtables = self.qtables

                # if (subsampling_config == 'keep' or subsampling_config is None) and (orig_subsampling is not None):
                    # options['subsampling'] = orig_subsampling
                # else:
                    # options['subsampling'] = subsampling_config

                # if (qtables_config == 'keep' or qtables_config is None) and (orig_qtables and 2 <= len(orig_qtables) <= 4):
                    # options['qtables'] = orig_qtables
                # else:
                    # options['qtables'] = qtables_config

    # if ext == '.png' and self.context.config.PNG_COMPRESSION_LEVEL is not None:
        # options['compress_level'] = self.context.config.PNG_COMPRESSION_LEVEL

    # if options['quality'] is None:
        # options['quality'] = self.context.config.QUALITY

    # if self.icc_profile is not None:
        # options['icc_profile'] = self.icc_profile

    # if self.context.config.PRESERVE_EXIF_INFO:
        # if self.exif is not None:
            # options['exif'] = self.exif

    # if self.image.mode == 'P' and self.transparency:
        # options['transparency'] = self.transparency

    try:
        # if ext == '.webp':
            # if self.image.mode not in ['RGB', 'RGBA']:
                # if self.image.mode == 'P':
                    # mode = 'RGBA'
                # else:
                    # mode = 'RGBA' if self.image.mode[-1] == 'A' else 'RGB'
                # self.image = self.image.convert(mode)

        # if ext in ['.png', '.gif'] and self.image.mode == 'CMYK':
            # self.image = self.image.convert('RGBA')
        img = details.metadata['image']

        img.format = FORMATS.get(details.mimetype, FORMATS['image/jpeg'])
        img.save(img_buffer, img.format, **options)
    except IOError:
        img.save(img_buffer, FORMATS.get(details.mimetype, FORMATS['image/jpeg']))

    results = img_buffer.getvalue()
    img_buffer.close()
    details.transformed_image = results
