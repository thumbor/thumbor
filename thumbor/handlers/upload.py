# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import mimetypes
import uuid
from urllib.parse import quote, unquote_to_bytes

from thumbor.engines import BaseEngine
from thumbor.handlers import ImageApiHandler


##
# Handler to upload images.
# This handler support only POST method, but images can be uploaded  :
#   - through multipart/form-data (designed for forms)
#   - or with the image content in the request body (rest style)
##
class ImageUploadHandler(ImageApiHandler):
    async def post(self):
        # Check if the image uploaded is a multipart/form-data
        if self.multipart_form_data():
            file_data = self.request.files["media"][0]
            body = file_data["body"]

            # Retrieve filename from 'filename' field
            filename = file_data["filename"]
        else:
            body = self.request.body

            # Retrieve filename from 'Slug' header
            filename = self.slug_filename()

        # Check if the image uploaded is valid
        if self.validate(body):
            # Use the default filename for the uploaded images. Clients
            # resolve "." and ".." as dot-segments, dropping the image id.
            if not filename or filename in (".", ".."):
                content_type = self.request.headers.get(
                    "Content-Type", BaseEngine.get_mimetype(body)
                )
                extension = mimetypes.guess_extension(
                    content_type.split(";", 1)[0], False
                )
                if extension is None:  # Content-Type is unknown, try with body
                    extension = mimetypes.guess_extension(
                        BaseEngine.get_mimetype(body), False
                    )
                if extension == ".jpe":
                    extension = (
                        ".jpg"  # Hack because mimetypes return .jpe by default
                    )
                if (
                    extension is None
                ):  # Even body is unknown, return an empty string to be contat
                    extension = ""
                filename = (
                    self.context.config.UPLOAD_DEFAULT_FILENAME + extension
                )

            # Build image id based on a random uuid (32 characters)
            image_id = str(uuid.uuid4().hex)
            await self.write_file(image_id, body)
            self.set_status(201)
            self.set_header("Location", self.location(image_id, filename))

    def multipart_form_data(self):
        if (
            "media" not in self.request.files
            or not self.request.files["media"]
        ):
            return False
        return True

    def slug_filename(self):
        slug = self.request.headers.get("Slug")
        if not slug:
            return slug
        # Tornado decodes header bytes as latin-1, while RFC 5023 defines
        # the Slug value as percent-encoded UTF-8.
        return unquote_to_bytes(slug.encode("latin1")).decode(
            "utf-8", "replace"
        )

    def location(self, image_id, filename):
        base_uri = self.request.uri
        # RFC 2231 multipart filenames can decode to lone surrogates, which
        # UTF-8 cannot encode.
        filename = quote(filename, safe="", errors="replace")
        return f"{base_uri}/{image_id}/{filename}"
