#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import tornado.web
import hashlib

from thumbor.crypto import Crypto
from thumbor.handlers import ContextHandler
from thumbor.context import RequestParameters

class CryptoHandler(ContextHandler):
    @tornado.web.asynchronous
    def get(self,
            crypto,
            image,
            security_key=None,
            **kw):

        cr = Crypto(security_key or self.context.server.security_key)

        try:
            opt = cr.decrypt(crypto)
        except ValueError:
            opt = None

        if not opt and not security_key and self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            security_key = self.storage.get_crypto(image)

            cr = Crypto(security_key or self.context.server.security_key)
            opt = cr.decrypt(crypto)

        image_hash = opt and opt.get('image_hash')
        image_hash = image_hash[1:] if image_hash and image_hash.startswith('/') else image_hash
        path_hash = hashlib.md5(image.encode('utf-8')).hexdigest()

        if not image_hash or image_hash != path_hash:
            self._error(404, 'Request denied because the specified image hash is not valid.')
            return

        opt['image'] = image

        self.context.request = RequestParameters(**opt)

        return self.execute_image_operations()

