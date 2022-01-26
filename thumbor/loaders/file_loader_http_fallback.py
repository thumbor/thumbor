#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.loaders import LoaderResult, file_loader, http_loader


async def load(context, path):
    # First attempt to load with file_loader
    result = await file_loader.load(context, path)

    if result.successful:
        return result

    # If file_loader failed try http_loader

    if not http_loader.validate(context, path):
        result = LoaderResult()
        result.successful = False
        result.error = LoaderResult.ERROR_BAD_REQUEST
        result.extras["reason"] = "Unallowed domain"
        result.extras["source"] = path

        return result

    return await http_loader.load(context, path)
