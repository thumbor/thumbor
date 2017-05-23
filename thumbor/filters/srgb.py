#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com


import thumbor.filters
from thumbor.filters import BaseFilter, filter_method
from thumbor.utils import logger
from thumbor.engines.pil import Engine as PILEngine

from io import BytesIO

try:
    from PIL import ImageCms
except:
    ImageCms = None

# Facebook version.
# See https://www.facebook.com/notes/facebook-engineering/under-the-hood-improving-facebook-photos/10150630639853920
tiny_srgb = bytearray([0, 0, 2, 12, 108, 99, 109, 115, 2, 16, 0, 0, 109, 110, 116, 114, 82, 71, 66, 32, 88, 89, 90, 32,
                       7, 220, 0, 1, 0, 25, 0, 3, 0, 41, 0, 57, 97, 99, 115, 112, 65, 80, 80, 76, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 246, 214, 0, 1, 0, 0, 0, 0, 211, 45,
                       108, 99, 109, 115, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 100, 101, 115, 99, 0, 0, 0,
                       252, 0, 0, 0, 94, 99, 112, 114, 116, 0, 0, 1, 92, 0, 0, 0, 11, 119, 116, 112, 116, 0, 0, 1, 104,
                       0, 0, 0, 20, 98, 107, 112, 116, 0, 0, 1, 124, 0, 0, 0, 20, 114, 88, 89, 90, 0, 0, 1, 144, 0, 0,
                       0, 20, 103, 88, 89, 90, 0, 0, 1, 164, 0, 0, 0, 20, 98, 88, 89, 90, 0, 0, 1, 184, 0, 0, 0, 20,
                       114, 84, 82, 67, 0, 0, 1, 204, 0, 0, 0, 64, 103, 84, 82, 67, 0, 0, 1, 204, 0, 0, 0, 64, 98, 84,
                       82, 67, 0, 0, 1, 204, 0, 0, 0, 64, 100, 101, 115, 99, 0, 0, 0, 0, 0, 0, 0, 3, 99, 50, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 116, 101, 120, 116, 0, 0, 0, 0, 70, 66, 0, 0, 88, 89,
                       90, 32, 0, 0, 0, 0, 0, 0, 246, 214, 0, 1, 0, 0, 0, 0, 211, 45, 88, 89, 90, 32, 0, 0, 0, 0, 0, 0,
                       3, 22, 0, 0, 3, 51, 0, 0, 2, 164, 88, 89, 90, 32, 0, 0, 0, 0, 0, 0, 111, 162, 0, 0, 56, 245, 0,
                       0, 3, 144, 88, 89, 90, 32, 0, 0, 0, 0, 0, 0, 98, 153, 0, 0, 183, 133, 0, 0, 24, 218, 88, 89, 90,
                       32, 0, 0, 0, 0, 0, 0, 36, 160, 0, 0, 15, 132, 0, 0, 182, 207, 99, 117, 114, 118, 0, 0, 0, 0, 0,
                       0, 0, 26, 0, 0, 0, 203, 1, 201, 3, 99, 5, 146, 8, 107, 11, 246, 16, 63, 21, 81, 27, 52, 33, 241,
                       41, 144, 50, 24, 59, 146, 70, 5, 81, 119, 93, 237, 107, 112, 122, 5, 137, 177, 154, 124, 172,
                       105, 191, 125, 211, 195, 233, 48, 255, 255])


class Filter(BaseFilter):
    phase = thumbor.filters.PHASE_AFTER_LOAD

    @filter_method()
    def srgb(self):
        if not isinstance(self.engine, PILEngine):
            logger.warn('Could not perform profileToProfile conversion: engine is not PIL engine')
            return

        if (ImageCms is None):
            logger.warn('ImageCms is not installed. Could not perform profileToProfile conversion')
            return

        image = self.engine.image

        embedded_profile = image.info.get('icc_profile')

        if not embedded_profile:
            logger.debug('Image does not have embedded profile. Assuming already in sRGB')
            return

        embedded_profile = BytesIO(embedded_profile)
        srgb_profile = BytesIO(tiny_srgb)

        output_mode = 'RGBA' if 'A' in image.mode else 'RGB'
        image = ImageCms.profileToProfile(image, embedded_profile, srgb_profile, renderingIntent=0,
                                          outputMode=output_mode)

        self.engine.image = image
        self.engine.icc_profile = image.info.get('icc_profile')
