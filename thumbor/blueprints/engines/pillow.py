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

from thumbor.blueprints.engines.pillow_extensions import PillowExtensions
from thumbor.lifecycle import Events


def plug_into_lifecycle():
    '''Plugs into thumbor's lifecycle'''
    Events.subscribe(Events.Imaging.before_transforming_image,
                     on_before_transforming_image)
    Events.subscribe(Events.Engine.resize, on_resize)
    Events.subscribe(Events.Imaging.after_transforming_image,
                     on_after_transforming_image)


@tornado.gen.coroutine
def on_before_transforming_image(sender, request, details):
    'Loads the image into PIL'
    try:
        img = PillowExtensions.create_image(details.source_image)
    except Image.DecompressionBombWarning:
        details.finish_early = True
        details.body = 'Image could not be loaded by PIL engine'
        details.status_code = 500
        return False

    details.metadata['icc_profile'] = img.info.get('icc_profile')

    details.metadata['transparency'] = img.info.get('transparency')
    details.metadata['exif'] = img.info.get('exif')

    details.metadata['subsampling'] = JpegImagePlugin.get_sampling(img)
    if details.metadata['subsampling'] == -1:  # n/a for this file
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
def on_resize(sender, details, width, height):
    'Handles the resize event'
    PillowExtensions.resize(details, width, height)


@tornado.gen.coroutine
def on_crop(sender, details, left, top, right, bottom):
    'Handles the crop event'
    PillowExtensions.crop(details, left, top, right, bottom)


@tornado.gen.coroutine
def on_after_transforming_image(sender, request, details):
    'Serializes the image after transforming'
    _serialize_image(details)


def _serialize_image(details):
    img = details.metadata['image']
    # returns image buffer in byte format.
    img_buffer = BytesIO()

    options = {
        'quality': details.metadata.get('quality', details.config.QUALITY),
    }

    _configure_jpeg(img, details, options)
    _configure_png(img, details, options)
    _ensure_quality(details, options)
    _get_additional_metadata(img, details, options)

    try:
        img = _handle_webp_conversion(img, details)
        img = _handle_cmyk_conversion(img, details)

        img.format = PillowExtensions.FORMATS.get(
            details.mimetype, PillowExtensions.FORMATS['image/jpeg'])
        img.save(img_buffer, img.format, **options)
    except IOError:
        img.save(img_buffer,
                 PillowExtensions.FORMATS.get(
                     details.mimetype, PillowExtensions.FORMATS['image/jpeg']))

    results = img_buffer.getvalue()
    img_buffer.close()
    details.transformed_image = results


def _configure_jpeg(img, details, options):
    if details.mimetype not in ['image/jpeg', 'image/jpg']:
        return

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
            # can't use 'keep' here as Pillow would try
            # to extract qtables/subsampling and fail
            options['quality'] = 0

            orig_subsampling = details.metadata.get('subsampling', None)
            orig_qtables = details.metadata.get('qtables', None)

            use_original_subsampling = (subsampling_config == 'keep' or
                                        subsampling_config is None)
            if use_original_subsampling and orig_subsampling is not None:
                options['subsampling'] = orig_subsampling
            else:
                options['subsampling'] = subsampling_config

            if (qtables_config == 'keep' or
                    qtables_config is None) and (orig_qtables and
                                                 2 <= len(orig_qtables) <= 4):
                options['qtables'] = orig_qtables
            else:
                options['qtables'] = qtables_config


def _configure_png(_img, details, options):
    if details.mimetype != 'image/png' or details.config.PNG_COMPRESSION_LEVEL is None:
        return

    options['compress_level'] = details.config.PNG_COMPRESSION_LEVEL


def _ensure_quality(details, options):
    if options['quality'] is None:
        options['quality'] = details.config.QUALITY


def _get_additional_metadata(img, details, options):
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


def _handle_webp_conversion(img, details):
    if details.mimetype != 'image/webp':
        return img

    if img.mode in ['RGB', 'RGBA']:
        return img

    mode = 'RGBA'
    # Not pallette and does not have alpha channel
    if img.mode != 'P' and img.mode[-1] != 'A':
        mode = 'RGB'
    return img.convert(mode)


def _handle_cmyk_conversion(img, details):
    if details.mimetype not in ['image/png', 'image/gif']:
        return img
    if img.mode != 'CMYK':
        return img

    return img.convert('RGBA')
