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


class HttpHandler(ContextHandler):

    delete_hash = r'(?:(?P<delete_hash>[^/]{28,})/)?'

    @classmethod
    def url_regex(cls):
        reg = ['/(?P<delete_type>(?:original|result))/']

        reg.append(cls.delete_hash)
        reg.append(Url.regex())

        return ''.join(reg)

    def delete_image(self, kw):
        delete_type = kw.pop('delete_type')
        url_signature = kw.pop('delete_hash')

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

        signer = Signer(self.context.server.security_key)

        url_to_validate = Url.encode_url(url).replace('/%s/' % url_signature, '/')
        valid = signer.validate(url_signature, url_to_validate)

        if not valid:
            self._error(404, 'Malformed URL: %s' % url)
            return

        if delete_type == 'original':
            if self.context.modules.storage and self.context.modules.storage.exists(self.context.request.image_url):
                self.context.modules.storage.remove(self.context.request.image_url)
            else:
                self._error(404)
                return
        else:
            self.context.request.url = self.context.request.url.replace('/%s/%s' % (delete_type, url_signature), '')
            self.context.request.image_url = self.context.request.image_url.replace('/%s/%s' % (delete_type, url_signature), '')
            if self.context.modules.result_storage and self.context.modules.result_storage.exists():
                self.context.modules.result_storage.remove()
            else:
                self._error(404)
                return

        self.set_status(204)
        self.finish()

    @tornado.web.asynchronous
    def delete(self, **kw):
        self.delete_image(kw)
