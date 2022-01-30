# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import re

from libthumbor.url import Url

from thumbor.filters import PHASE_PRE_LOAD, BaseFilter, filter_method
from thumbor.point import FocalPoint

MAX_LEVEL = 10


class Filter(BaseFilter):
    phase = PHASE_PRE_LOAD

    domain_regex = re.compile(r"^(https?://)?.*?/")
    url_regex = re.compile(Url.regex())

    def parse_url(self, url):
        level = 0
        while level < MAX_LEVEL:
            url = self.domain_regex.sub("", url)
            result = self.url_regex.match(url)
            if not result:
                return None

            parts = result.groupdict()
            image = parts.get("image", None)

            if not (
                image
                and (parts.get("hash", None) or parts.get("unsafe", None))
            ):
                return None

            top, right, left, bottom = (
                parts.get("crop_top", None),
                parts.get("crop_right", None),
                parts.get("crop_left", None),
                parts.get("crop_bottom", None),
            )
            if top and right and left and bottom:
                return (image, top, right, left, bottom)

            url = image
            level += 1

        return None

    @filter_method()
    async def extract_focal(self):
        parts = self.parse_url(self.context.request.image_url)
        if parts:
            image, top, right, left, bottom = parts
            top, right, left, bottom = (
                int(top),
                int(right),
                int(left),
                int(bottom),
            )

            width = right - left
            height = bottom - top
            self.context.request.focal_points.append(
                FocalPoint.from_square(
                    left, top, width, height, origin="Original Extraction"
                )
            )
            self.context.request.image_url = image
