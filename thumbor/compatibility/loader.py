#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.compatibility import compatibility_get


async def load(context, path):
    loader = context.modules.compatibility_legacy_loader
    if loader is None:
        raise RuntimeError(
            "The 'COMPATIBILITY_LEGACY_LOADER' configuration should point "
            "to a valid loader when using compatibility loader."
        )

    return await compatibility_get(context, path, func=loader.load)
