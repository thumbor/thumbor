#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com
import datetime

from thumbor.engines import BaseEngine
from thumbor.handlers import ImageApiHandler


##
# Handler to retrieve or modify existing images
# This handler support GET, PUT and DELETE method to manipulate existing images
##
class ImageResourceHandler(ImageApiHandler):
    async def check_resource(self, file_id):
        file_id = file_id[: self.context.config.MAX_ID_LENGTH]
        # Check if image exists
        exists = await self.context.modules.storage.exists(file_id)

        if exists:
            body = await self.context.modules.storage.get(file_id)
            self.set_status(200)

            mime = BaseEngine.get_mimetype(body)
            if mime:
                self.set_header("Content-Type", mime)

            max_age = self.context.config.MAX_AGE
            if max_age:
                self.set_header(
                    "Cache-Control", "max-age=" + str(max_age) + ",public"
                )
                self.set_header(
                    "Expires",
                    datetime.datetime.utcnow()
                    + datetime.timedelta(seconds=max_age),
                )
            self.write(body)
            self.finish()
        else:
            self._error(404, "Image not found at the given URL")

    async def put(self, file_id):
        file_id = file_id[: self.context.config.MAX_ID_LENGTH]
        # Check if image overwriting is allowed
        if not self.context.config.UPLOAD_PUT_ALLOWED:
            self._error(405, "Unable to modify an uploaded image")
            return

        # Check if the image uploaded is valid
        if self.validate(self.request.body):
            await self.write_file(file_id, self.request.body)
            self.set_status(204)

    async def delete(self, file_id):
        file_id = file_id[: self.context.config.MAX_ID_LENGTH]
        # Check if image deleting is allowed
        if not self.context.config.UPLOAD_DELETE_ALLOWED:
            self._error(405, "Unable to delete an uploaded image")
            return

        # Check if image exists
        exists = await self.context.modules.storage.exists(file_id)
        if exists:
            await self.context.modules.storage.remove(file_id)
            self.set_status(204)
        else:
            self._error(404, "Image not found at the given URL")

    async def get(self, file_id):
        await self.check_resource(file_id)

    async def head(self, file_id):
        await self.check_resource(file_id)
