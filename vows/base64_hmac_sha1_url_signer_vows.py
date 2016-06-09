# -*- coding: utf-8 -*-

import hashlib
import base64
import hmac
from pyvows import Vows, expect
from thumbor.url_signers.base64_hmac_sha1 import UrlSigner


@Vows.batch
class Base64HmacSha1UrlSignerVows(Vows.Context):
    def topic(self):
        return UrlSigner(security_key="something")

    def should_be_signer_instance(self, topic):
        expect(topic).to_be_instance_of(UrlSigner)

    def should_have_security_key(self, topic):
        expect(topic.security_key).to_equal('something')

    class Sign(Vows.Context):
        def topic(self, signer):
            url = '10x11:12x13/-300x-300/center/middle/smart/some/image.jpg'
            expected = base64.urlsafe_b64encode(
                hmac.new(
                    'something', unicode(url).encode('utf-8'), hashlib.sha1
                ).digest()
            )
            return (signer.signature(url), expected)

        def should_equal_encrypted_string(self, test_data):
            topic, expected = test_data
            expect(topic).to_equal(expected)
