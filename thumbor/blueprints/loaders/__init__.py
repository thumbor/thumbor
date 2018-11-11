#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.lifecycle import Events


class Loader:
    def __init__(self):
        Events.subscribe(Events.Imaging.load_source_image, self.load_source_image)

    async def load_source_image(self, sender, request, details):
        res = await self.on_load_source_image(request, details)

        return res

    async def on_load_source_image(self, request, details):
        raise NotImplementedError()
