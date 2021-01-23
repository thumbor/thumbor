#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import asyncio


async def compatibility_get(*args, **kw):
    func = kw.pop("func", None)
    if func is None:
        raise RuntimeError(
            "'func' argument can't be None when calling thumbor's compatibility layer."
        )

    loop = asyncio.get_event_loop()
    queue = asyncio.Queue()

    def put(*args):
        loop.call_soon_threadsafe(queue.put_nowait, args)

    func(*args, **kw, callback=put)

    result = await queue.get()
    if isinstance(result, (tuple, list)) and len(result) == 1:
        result = result[0]

    return result
