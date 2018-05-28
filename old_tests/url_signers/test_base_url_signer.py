#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from unittest import TestCase

from preggy import expect

from thumbor.url_signers import (
    BaseUrlSigner
)


class BaseSignerTestCase(TestCase):
    def test_can_create_signer(self):
        signer = BaseUrlSigner(security_key="something")
        expect(signer).to_be_instance_of(BaseUrlSigner)
        expect(signer.security_key).to_equal('something')

    def test_can_create_unicode_signer(self):
        signer = BaseUrlSigner(security_key=u"téste")
        expect(signer).to_be_instance_of(BaseUrlSigner)
        expect(signer.security_key).to_equal('t\xc3\xa9ste')

    def test_can_validate_url(self):
        class TestSigner(BaseUrlSigner):
            def signature(self, url):
                return "%s+1" % url

        signer = TestSigner(security_key=u"téste")
        expect(signer.validate("http://www.test.com+1", "http://www.test.com")).to_be_true()

    def test_has_abstract_method(self):
        signer = BaseUrlSigner(security_key=u"téste")

        with expect.error_to_happen(NotImplementedError):
            signer.signature("test-url")
