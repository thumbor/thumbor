#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.ext.filters import _nine_patch
from thumbor.filters import BaseFilter, filter_method
from thumbor.loaders import LoaderResult


class Filter(BaseFilter):
    regex = r"(?:frame\((?P<url>.*?))"

    async def on_image_ready(self, buffer):
        self.nine_patch_engine.load(buffer, None)
        self.nine_patch_engine.enable_alpha()
        self.engine.enable_alpha()

        (
            nine_patch_mode,
            nine_patch_data,
        ) = self.nine_patch_engine.image_data_as_rgb()
        padding = _nine_patch.get_padding(
            nine_patch_mode,
            nine_patch_data,
            self.nine_patch_engine.size[0],
            self.nine_patch_engine.size[1],
        )

        self.handle_padding(padding)

        mode, data = self.engine.image_data_as_rgb()

        if mode != nine_patch_mode:
            raise RuntimeError(
                f"Image mode mismatch: {mode} != {nine_patch_mode}"
            )

        imgdata = _nine_patch.apply(
            mode,
            data,
            self.engine.size[0],
            self.engine.size[1],
            nine_patch_data,
            self.nine_patch_engine.size[0],
            self.nine_patch_engine.size[1],
        )
        self.engine.set_image_data(imgdata)

    def handle_padding(self, padding):
        """Pads the image with transparent pixels if necessary."""
        left = padding[0]
        top = padding[1]
        right = padding[2]
        bottom = padding[3]

        offset_x = 0
        offset_y = 0
        new_width = self.engine.size[0]
        new_height = self.engine.size[1]

        if left > 0:
            offset_x = left
            new_width += left
        if top > 0:
            offset_y = top
            new_height += top
        if right > 0:
            new_width += right
        if bottom > 0:
            new_height += bottom
        new_engine = self.context.modules.engine.__class__(self.context)
        new_engine.image = new_engine.gen_image(
            (new_width, new_height), "#fff"
        )
        new_engine.enable_alpha()
        new_engine.paste(self.engine, (offset_x, offset_y))
        self.engine.image = new_engine.image

    async def on_fetch_done(self, result):
        # TODO if result.successful is False how can the error be handled?
        if isinstance(result, LoaderResult):
            buffer = result.buffer
        else:
            buffer = result

        self.nine_patch_engine.load(buffer, None)
        await self.storage.put(self.url, self.nine_patch_engine.read())
        await self.storage.put_crypto(self.url)
        await self.on_image_ready(buffer)

    @filter_method(BaseFilter.String)
    async def frame(self, url):
        self.url = url
        self.nine_patch_engine = self.context.modules.engine.__class__(
            self.context
        )
        self.storage = self.context.modules.storage

        buffer = await self.storage.get(self.url)
        if buffer is not None:
            return await self.on_image_ready(buffer)

        result = await self.context.modules.loader.load(self.context, self.url)
        await self.on_fetch_done(result)
