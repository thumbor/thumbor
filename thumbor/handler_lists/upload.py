#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from typing import Any, cast

from thumbor.handler_lists import HandlerList


def get_handlers(context: Any) -> HandlerList:
    is_upload_enabled = cast(bool, context.config.UPLOAD_ENABLED)
    if not is_upload_enabled:
        return []

    return [
        (r"/image", context.modules.upload_handler, {"context": context}),
        (
            r"/image/(.*)",
            context.modules.resource_handler,
            {"context": context},
        ),
    ]
