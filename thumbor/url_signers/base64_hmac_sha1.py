# -*- coding: utf-8 -*-

import base64
import hashlib
import hmac
from thumbor.url_signers import BaseUrlSigner


class UrlSigner(BaseSigner):
    """Validate urls and sign them using base64 hmac-sha1
    """

    def validate(self, actual_signature, url):
        url_signature = self.signature(url)
        return url_signature == actual_signature

    def signature(self, url):
        return base64.urlsafe_b64encode(hmac.new(self.security_key, unicode(url).encode('utf-8'), hashlib.sha1).digest())
