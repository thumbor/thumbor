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
from PIL import Image, JpegImagePlugin, ImageSequence

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
        img = Image.open(BytesIO(details.source_image))
    except Image.DecompressionBombWarning as e:
        details.finish_early = True
        details.body = 'Image could not be loaded by PIL engine'
        details.status_code = 500
        return False

    details.metadata['icc_profile'] = img.info.get('icc_profile')

    details.metadata['transparency'] = img.info.get('transparency')
    details.metadata['exif'] = img.info.get('exif')

    details.metadata['subsampling'] = JpegImagePlugin.get_sampling(img)
    if (details.metadata['subsampling'] == -1):  # n/a for this file
        details.metadata['subsampling'] = None
    details.metadata['qtables'] = getattr(img, 'quantization', None)

    if details.config.ALLOW_ANIMATED_GIFS and details.mimetype == 'image/gif':
        frames = []
        for frame in ImageSequence.Iterator(img):
            frames.append(frame.convert('P'))
        img.seek(0)
        details.metadata['frame_count'] = len(frames)
        return frames

    details.metadata['image'] = img
    return True


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
    img = details.metadata['image']
    # returns image buffer in byte format.
    img_buffer = BytesIO()

    options = {
        'quality': details.config.QUALITY,
    }
    if details.mimetype in ['image/jpeg', 'image/jpg']:
        options['optimize'] = True
        if details.config.PROGRESSIVE_JPEG:
            # Can't simply set options['progressive'] to the value
            # of details.config.PROGRESSIVE_JPEG because save
            # operates on the presence of the key in **options, not
            # the value of that setting.
            options['progressive'] = True

        if img.mode != 'RGB':
            img = img.convert('RGB')
        else:
            subsampling_config = details.config.PILLOW_JPEG_SUBSAMPLING
            qtables_config = details.config.PILLOW_JPEG_QTABLES

            if subsampling_config is not None or qtables_config is not None:
                options['quality'] = 0  # can't use 'keep' here as Pillow would try to extract qtables/subsampling and fail
                orig_subsampling = details.metadata.get('subsampling', None)
                orig_qtables = details.metadata.get('qtables', None)

                if (subsampling_config == 'keep' or subsampling_config is None) and (orig_subsampling is not None):
                    options['subsampling'] = orig_subsampling
                else:
                    options['subsampling'] = subsampling_config

                if (qtables_config == 'keep' or qtables_config is None) and (orig_qtables and 2 <= len(orig_qtables) <= 4):
                    options['qtables'] = orig_qtables
                else:
                    options['qtables'] = qtables_config

    if details.mimetype == 'image/png' and details.config.PNG_COMPRESSION_LEVEL is not None:
        options['compress_level'] = details.config.PNG_COMPRESSION_LEVEL

    if options['quality'] is None:
        options['quality'] = details.config.QUALITY

    icc = details.metadata.get('icc_profile', None)
    if icc is not None:
        options['icc_profile'] = icc

    if details.config.PRESERVE_EXIF_INFO:
        exif = details.metadata.get('exif', None)
        if exif is not None:
            options['exif'] = exif

    transparency = details.metadata.get('transparency', None)
    if img.mode == 'P' and transparency is not None:
        options['transparency'] = transparency

    try:
        if details.mimetype == 'image/webp':
            if img.mode not in ['RGB', 'RGBA']:
                if img.mode == 'P':
                    mode = 'RGBA'
                else:
                    mode = 'RGBA' if img.mode[-1] == 'A' else 'RGB'
                img = img.convert(mode)

        if details.mimetype in ['image/png', 'image/gif'] and img.mode == 'CMYK':
            img = img.convert('RGBA')

        img.format = FORMATS.get(details.mimetype, FORMATS['image/jpeg'])
        img.save(img_buffer, img.format, **options)
    except IOError:
        img.save(img_buffer, FORMATS.get(details.mimetype, FORMATS['image/jpeg']))

    results = img_buffer.getvalue()
    img_buffer.close()
    details.transformed_image = results
