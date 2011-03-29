#!/usr/bin/python
# -*- coding: utf-8 -*-

from thumbor.crypto import Crypto

def test_can_create_crypto():
    crypto = Crypto(salt="something")

    assert crypto
    assert crypto.salt == "somethingsomethingsometh"

def test_crypto_encrypts():
    crypto = Crypto(salt="something")

    encrypted = crypto.encrypt(width=300, height=300, smart=True)

    assert encrypted == '2GyGjZYFNENBkuBhhMTs9g=='

def test_decrypt():
    crypto = Crypto(salt="something")

    encrypted = crypto.encrypt(width=300, height=200, smart=True)

    decrypted = crypto.decrypt(encrypted)

    assert decrypted['width'] == 300
    assert decrypted['height'] == 200
    assert decrypted['smart'] == True

def test_decrypting_with_wrong_key_fails():

    crypto = Crypto(salt="something")

    encrypted = crypto.encrypt(width=300, height=200, smart=True)

    crypto = Crypto(salt="simething")

    decrypted = crypto.decrypt(encrypted)

    assert decrypted is None

