#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from urllib.parse import quote, unquote

from thumbor.context import RequestParameters
from thumbor.handlers import ContextHandler


class ImagingHandler(ContextHandler):
    def compute_etag(self):
        if self.context.config.ENABLE_ETAGS:
            return super().compute_etag()
        return None

    async def check_image(
        self, kwargs
    ):  # pylint: disable=too-many-return-statements
        if self.context.config.MAX_ID_LENGTH > 0:
            # Check if an image with an uuid exists in storage
            exists = await self.context.modules.storage.exists(
                kwargs["image"][: self.context.config.MAX_ID_LENGTH]
            )
            if exists:
                kwargs["image"] = kwargs["image"][
                    : self.context.config.MAX_ID_LENGTH
                ]

        url = self.request.path

        kwargs["image"] = quote(kwargs["image"].encode("utf-8"))
        if not self.validate(kwargs["image"]):
            self._error(
                400, "No original image was specified in the given URL"
            )
            return

        kwargs["request"] = self.request
        self.context.request = RequestParameters(**kwargs)

        has_none = (
            not self.context.request.unsafe and not self.context.request.hash
        )
        has_both = self.context.request.unsafe and self.context.request.hash

        if has_none or has_both:
            self._error(
                400, f"URL does not have hash or unsafe, or has both: {url}"
            )
            return

        if (
            self.context.request.unsafe
            and not self.context.config.ALLOW_UNSAFE_URL
        ):
            self._error(
                400,
                f"URL has unsafe but unsafe is not allowed by the config: {url}",
            )
            return

        if self.context.config.USE_BLACKLIST:
            blacklist = await self.get_blacklist_contents()
            if self.context.request.image_url in blacklist:
                self._error(
                    400,
                    f"Source image url has been blacklisted: {self.context.request.image_url}",
                )
                return

        url_signature = self.context.request.hash
        if url_signature:
            signer = self.context.modules.url_signer(
                self.context.server.security_key
            )

            try:
                quoted_hash = quote(self.context.request.hash)
            except KeyError:
                self._error(400, f"Invalid hash: {self.context.request.hash}")
                return

            url_to_validate = url.replace(
                f"/{self.context.request.hash}/", ""
            ).replace(f"/{quoted_hash}/", "")

            valid = signer.validate(
                unquote(url_signature).encode(), url_to_validate
            )

            if (
                not valid
                and self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE
            ):
                # Retrieves security key for this image if it has been seen before
                security_key = await self.context.modules.storage.get_crypto(
                    self.context.request.image_url
                )
                if security_key is not None:
                    signer = self.context.modules.url_signer(security_key)
                    valid = signer.validate(
                        url_signature.encode(), url_to_validate
                    )

            if not valid:
                self._error(400, f"Malformed URL: {url}")
                return

        return await self.execute_image_operations()

    async def get(self, **kw):
        return await self.check_image(kw)

    async def head(self, **kw):
        return await self.check_image(kw)
