#!/usr/bin/python
# -*- coding: utf-8 -*-
# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
from thumbor.filters import BaseFilter, filter_method


class Filter(BaseFilter):
    @filter_method(BaseFilter.Boolean)
    async def autojpg(self, enabled=True):
        self.context.request.auto_png_to_jpg = enabled
