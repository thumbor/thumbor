#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.loaders import file_loader
from thumbor.loaders import http_loader
from tornado import gen


@gen.coroutine
def load(context, path):
    # First attempt to load with file_loader
    result = yield file_loader.load(context, path)
    if not result.successful:
        # If file_loader failed try http_loader
        result = yield http_loader.load(context, path)
    raise gen.Return(result)
