#!/usr/bin/python
# -*- coding: utf-8 -*-

from thumbor.crypto import Crypto

def test_can_create_crypto():
    crypto = Crypto(salt="something")

    assert crypto
    assert crypto.salt == "somethingsomethingsometh"

def test_crypto_encrypts():
    crypto = Crypto(salt="something")

    encrypted = crypto.encrypt(width=300,
                               height=300,
                               smart=True,
                               flip_horizontal=True,
                               flip_vertical=True,
                               halign="center",
                               valign="middle",
                               crop_left=10,
                               crop_top=11,
                               crop_right=12,
                               crop_bottom=13)

    assert encrypted == 'EdM9L9a8brwnJ-n7Og-yxOJLvf0GHvxFCKknHz_elOc='

def test_decrypt():
    crypto = Crypto(salt="something")

    encrypted = crypto.encrypt(width=300,
                               height=200,
                               smart=True,
                               flip_horizontal=True,
                               flip_vertical=True,
                               halign="center",
                               valign="middle",
                               crop_left=10,
                               crop_top=11,
                               crop_right=12,
                               crop_bottom=13)

    decrypted = crypto.decrypt(encrypted)

    assert decrypted['width'] == 300
    assert decrypted['height'] == 200
    assert decrypted['smart'] == True

def test_decrypting_with_wrong_key_fails():

    crypto = Crypto(salt="something")

    encrypted = crypto.encrypt(width=300,
                               height=200,
                               smart=True,
                               flip_horizontal=True,
                               flip_vertical=True,
                               halign="center",
                               valign="middle",
                               crop_left=10,
                               crop_top=11,
                               crop_right=12,
                               crop_bottom=13)

    crypto = Crypto(salt="simething")

    decrypted = crypto.decrypt(encrypted)

    assert decrypted is None

def test_encdec_with_extra_args():

    crypto = Crypto(salt="something")

    encrypted = crypto.encrypt(width=300,
                               height=200,
                               smart=False,
                               flip_horizontal=True,
                               flip_vertical=True,
                               halign="center",
                               valign="middle",
                               crop_left=10,
                               crop_top=11,
                               crop_right=12,
                               crop_bottom=13)

    decrypted = crypto.decrypt(encrypted)

    assert decrypted['width'] == 300
    assert decrypted['height'] == 200
    assert not decrypted['smart']
    assert decrypted['horizontal_flip']
    assert decrypted['vertical_flip']

    assert decrypted['halign'] == "center"
    assert decrypted['valign'] == "middle"

    assert decrypted['crop']
    assert decrypted['crop']['left'] == 10
    assert decrypted['crop']['top'] == 11
    assert decrypted['crop']['right'] == 12
    assert decrypted['crop']['bottom'] == 13

