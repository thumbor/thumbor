#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import tornado.web

from thumbor.handlers import ContextHandler
from thumbor.context import RequestParameters
from thumbor.crypto import Cryptor, Signer
from thumbor.utils import logger
from thumbor.url import Url


class ImagingHandler(ContextHandler):

    @tornado.web.asynchronous
    def get(self, **kw):
        # Check if an image with an uuid exists in storage
        if self.context.modules.storage.exists(kw['image'][:32]):
            kw['image'] = kw['image'][:32]

        url = self.request.uri

        if not self.validate(kw['image']):
            self._error(404, 'No original image was specified in the given URL')
            return

        kw['request'] = self.request

        self.context.request = RequestParameters(**kw)

        has_none = not self.context.request.unsafe and not self.context.request.hash
        has_both = self.context.request.unsafe and self.context.request.hash

        if has_none or has_both:
            self._error(404, 'URL does not have hash or unsafe, or has both: %s' % url)
            return

        if self.context.request.unsafe and not self.context.config.ALLOW_UNSAFE_URL:
            self._error(404, 'URL has unsafe but unsafe is not allowed by the config: %s' % url)
            return

        url_signature = self.context.request.hash
        if url_signature:
            signer = Signer(self.context.server.security_key)

            url_to_validate = Url.encode_url(url).replace('/%s/' % self.context.request.hash, '')
            valid = signer.validate(url_signature, url_to_validate)

            if not valid and self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
                # Retrieves security key for this image if it has been seen before
                security_key = self.context.modules.storage.get_crypto(self.context.request.image_url)
                if security_key is not None:
                    signer = Signer(security_key)
                    valid = signer.validate(url_signature, url_to_validate)

            if not valid:
                is_valid = True
                if self.context.config.ALLOW_OLD_URLS:
                    cr = Cryptor(self.context.server.security_key)
                    options = cr.get_options(self.context.request.hash, self.context.request.image_url)
                    if options is None:
                        is_valid = False
                    else:
                        options['request'] = self.request
                        self.context.request = RequestParameters(**options)
                        logger.warning(
                            'OLD FORMAT URL DETECTED!!! This format of URL will be discontinued in ' +
                            'upcoming versions. Please start using the new format as soon as possible. ' +
                            'More info at https://github.com/globocom/thumbor/wiki/3.0.0-release-changes'
                        )
                else:
                    is_valid = False

                if not is_valid:
                    self._error(404, 'Malformed URL: %s' % url)
                    return

        return self.execute_image_operations()
