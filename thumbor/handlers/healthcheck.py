#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.handlers import BaseHandler


class HealthcheckHandler(BaseHandler):
    async def get(self):
        self.set_header("Cache-Control", "no-cache")
        self.write("WORKING")

    async def head(self):
        self.set_header("Cache-Control", "no-cache")
        self.set_status(200)
