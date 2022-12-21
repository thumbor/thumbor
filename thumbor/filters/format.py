#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.filters import BaseFilter, filter_method
from thumbor.utils import logger

ALLOWED_FORMATS = ["png", "jpeg", "jpg", "gif", "webp", "avif", "heic", "heif"]


class Filter(BaseFilter):
    @filter_method(BaseFilter.String)
    async def format(self, file_format):
        if file_format.lower() not in ALLOWED_FORMATS:
            logger.debug("Format not allowed: %s", file_format.lower())
            self.context.request.format = None
        else:
            logger.debug("Format specified: %s", file_format.lower())
            self.context.request.format = file_format.lower()
