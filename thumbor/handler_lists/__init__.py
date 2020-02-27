#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from tornado.routing import _RuleList

BUILTIN_HANDLERS = [
    "thumbor.handler_lists.healthcheck",
    "thumbor.handler_lists.upload",
    "thumbor.handler_lists.blacklist",
]

HandlerList = _RuleList
