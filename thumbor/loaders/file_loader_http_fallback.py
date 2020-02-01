#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.loaders import file_loader, http_loader


async def load(context, path):
    # First attempt to load with file_loader
    result = await file_loader.load(context, path)
    if result.successful:
        return result

    # If file_loader failed try http_loader
    return await http_loader.load(context, path)
