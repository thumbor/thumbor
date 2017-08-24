# -*- coding: utf-8 -*-

import base64
import hashlib
import hmac
from thumbor.url_signers import BaseUrlSigner

try:
    unicode        # Python 2
except NameError:
    unicode = str  # Python 3


class UrlSigner(BaseUrlSigner):
    """Validate urls and sign them using base64 hmac-sha1
    """

    def signature(self, url):
        return base64.urlsafe_b64encode(
            hmac.new(
                self.security_key, unicode(url).encode('utf-8'), hashlib.sha1
            ).digest()
        )
