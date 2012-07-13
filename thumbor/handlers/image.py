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

class ImageProcessHandler(ContextHandler):

    @tornado.web.asynchronous
    def get(self, **kw):
        url = self.request.uri

        if not self.validate(kw['image']):
            self._error(404, 'No original image was specified in the given URL')
            return

        self.context.request = RequestParameters(**kw)

        self.context.request.unsafe = self.context.request.unsafe == 'unsafe'

        if (self.request.query):
            self.context.request.image_url += '?%s' % self.request.query

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
            url_to_validate = url.replace('/%s/' % self.context.request.hash, '')
            security_key = None
            valid = False

            if self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
                security_key = self.context.modules.storage.get_crypto(self.context.request.image_url)
            else
                security_key = self.context.server.security_key

            if security_key is not None:
                valid = Signer(security_key).validate(url_signature, url_to_validate)

            if not valid:
                if self.context.config.ALLOW_OLD_URLS:
                    cr = Cryptor(self.context.server.security_key)
                    options = cr.get_options(self.context.request.hash, self.context.request.image_url)

                    if options is not None:
                        self.context.request = RequestParameters(**options)
                        valid = True
                        logger.warning('OLD FORMAT URL DETECTED!!! This format of URL will be discontinued in upcoming versions. Please start using the new format as soon as possible. More info at https://github.com/globocom/thumbor/wiki/3.0.0-release-changes')

            if not valid:
                self._error(404, 'Malformed URL: %s' % url)
                return

        return self.execute_image_operations()
