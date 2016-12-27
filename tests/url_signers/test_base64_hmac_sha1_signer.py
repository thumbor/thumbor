#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import base64
import hmac
import hashlib
from unittest import TestCase

from preggy import expect

from thumbor.url_signers.base64_hmac_sha1 import (
    UrlSigner
)


class Base64HmacSha1UrlSignerTestCase(TestCase):
    def test_can_create_signer(self):
        signer = UrlSigner(security_key="something")
        expect(signer).to_be_instance_of(UrlSigner)
        expect(signer.security_key).to_equal('something')

    def test_can_sign_url(self):
        signer = UrlSigner(security_key="something")
        url = '10x11:12x13/-300x-300/center/middle/smart/some/image.jpg'
        expected = base64.urlsafe_b64encode(
            hmac.new(
                'something', unicode(url).encode('utf-8'), hashlib.sha1
            ).digest()
        )
        actual = signer.signature(url)
        expect(actual).to_equal(expected)
