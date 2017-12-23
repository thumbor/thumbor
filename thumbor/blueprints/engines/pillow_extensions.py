#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com
'''
Raw Pillow operations.
'''

from io import BytesIO

from PIL import Image


class PillowExtensions:
    FORMATS = {
        'image/tif': 'PNG',  # serve tif as png
        'image/jpg': 'JPEG',
        'image/jpeg': 'JPEG',
        'image/gif': 'GIF',
        'image/png': 'PNG',
        'image/webp': 'WEBP'
    }

    @staticmethod
    def create_image(img):
        return Image.open(BytesIO(img))

    @staticmethod
    def crop(details, left, top, right, bottom):
        'Crops the image according to the specified dimensions'
        img = details['image']
        img = img.crop((int(left), int(top), int(right), int(bottom)))
        details.metadata['image'] = img

    @staticmethod
    def get_resize_filter(details):
        'Gets the best resize filter according to image'
        config = details.config

        resample = 'LANCZOS'
        if config.PILLOW_RESAMPLING_FILTER is not None:
            resample = config.PILLOW_RESAMPLING_FILTER

        available = {
            'LANCZOS': Image.LANCZOS,
            'NEAREST': Image.NEAREST,
            'BILINEAR': Image.BILINEAR,
            'BICUBIC': Image.BICUBIC,
        }

        if hasattr(Image, 'HAMMING'):
            available['HAMMING'] = Image.HAMMING

        return available.get(resample.upper(), Image.LANCZOS)

    @staticmethod
    def resize(details, width, height):
        'Resizes the image according to the specified dimensions'
        img = details.metadata['image']

        # Indexed color modes (such as 1 and P) will be forced to use a
        # nearest neighbor resampling algorithm. So we convert them to
        # RGBA mode before resizing to avoid nasty scaling artifacts.
        original_mode = img.mode
        if img.mode in ['1', 'P']:
            # logger.debug('converting image from 8-bit/1-bit palette to 32-bit RGBA for resize')
            img = img.convert('RGBA')

        resample = PillowExtensions.get_resize_filter(details)
        img = img.resize((int(width), int(height)), resample)

        # 1 and P mode images will be much smaller if converted back to
        # their original mode. So let's do that after resizing. Get $$.
        if original_mode != img.mode:
            img = img.convert(original_mode)

        details.metadata['image'] = img
