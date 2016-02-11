# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import re

from thumbor.filters import BaseFilter, filter_method, PHASE_PRE_LOAD
from thumbor.point import FocalPoint


class Filter(BaseFilter):
    phase = PHASE_PRE_LOAD

    focal_regex = re.compile("(\d+)x(\d+):(\d+)x(\d+)")

    @filter_method(BaseFilter.String)
    def focal(self, focal_string):
        left, top, right, bottom = self.focal_regex.match(focal_string).groups()
        left, top, right, bottom = int(left), int(top), int(right), int(bottom)
        width = right - left
        height = bottom - top

        if width and height:
            self.context.request.focal_points.append(
                FocalPoint.from_square(left, top, width, height, origin="Explicit")
            )
