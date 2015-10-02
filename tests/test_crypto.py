#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from unittest import TestCase
import hashlib
import copy
import mock

from preggy import expect

from thumbor.crypto import (
    Cryptor
)

from tests.fixtures.crypto_fixtures import DECRYPT_TESTS, BASE_PARAMS


class CryptoTestCase(TestCase):
    def setUp(self, *args, **kw):
        super(CryptoTestCase, self).setUp(*args, **kw)
        self.cryptor = Cryptor(security_key="something")
        self.cryptor.context = mock.Mock(
            config=mock.Mock(
                STORES_CRYPTO_KEY_FOR_EACH_IMAGE=False
            ),
        )

    def test_can_create_crypto_with_key(self):
        cryptor = Cryptor("key")
        expect(cryptor).not_to_be_null()
        expect(cryptor.security_key).to_equal("keykeykeykeykeyk")

    def test_can_encrypt(self):
        encrypted = self.cryptor.encrypt(
            width=300,
            height=300,
            smart=True,
            adaptive=False,
            full=False,
            fit_in=False,
            flip_horizontal=True,
            flip_vertical=True,
            halign="center",
            valign="middle",
            trim=True,
            crop_left=10,
            crop_top=11,
            crop_right=12,
            crop_bottom=13,
            filters='some_filter()',
            image="/some/image.jpg"
        )

        encrypted_str = "hELdyDzyYtjXU5GhGxJVHjRvGrSP_iYKnIQbq_MuVq86rSObCeJvo2iXFRUjLgs" \
            "U9wDzhqK9J_SHmpxDJHW_rBD8eilO26x2M_hzJfGB-V9cGF65GO_7CgJXI8Ktw188"

        expect(encrypted).to_equal(encrypted_str)

    def test_can_decrypt(self):
        encrypted_str = "hELdyDzyYtjXU5GhGxJVHjRvGrSP_iYKnIQbq_MuVq86rSObCeJvo2iXFRUjLgs" \
            "U9wDzhqK9J_SHmpxDJHW_rBD8eilO26x2M_hzJfGB-V9cGF65GO_7CgJXI8Ktw188"

        decrypted = self.cryptor.decrypt(encrypted_str)

        expect(decrypted).not_to_be_null()
        expect(decrypted).not_to_be_an_error()
        expect(decrypted).not_to_be_empty()
        expect(decrypted['width']).to_equal(300)
        expect(decrypted['height']).to_equal(300)
        expect(decrypted['smart']).to_be_true()
        expect(decrypted['fit_in']).to_be_false()
        expect(decrypted['horizontal_flip']).to_be_true()
        expect(decrypted['vertical_flip']).to_be_true()
        expect(decrypted['halign']).to_equal('center')
        expect(decrypted['valign']).to_equal('middle')
        expect(decrypted['crop']['left']).to_equal(10)
        expect(decrypted['crop']['top']).to_equal(11)
        expect(decrypted['crop']['right']).to_equal(12)
        expect(decrypted['crop']['bottom']).to_equal(13)
        expect(decrypted['filters']).to_equal('some_filter()')

        image_hash = hashlib.md5('/some/image.jpg').hexdigest()
        expect(decrypted['image_hash']).to_equal(image_hash)

    def test_decrypting_with_wrong_key(self):
        encrypted_str = "hELdyDzyYtjXU5GhGxJVHjRvGrSP_iYKnIQbq_MuVq86rSObCeJvo2iXFRUjLgs" \
            "U9wDzhqK9J_SHmpxDJHW_rBD8eilO26x2M_hzJfGB-V9cGF65GO_7CgJXI8Ktw188"

        cryptor = Cryptor(security_key="simething")
        wrong = cryptor.decrypt(encrypted_str)
        right = self.cryptor.decrypt(encrypted_str)
        expect(wrong['image_hash']).not_to_equal(str(right['image_hash']))

    def test_get_options(self):
        encrypted_str = "hELdyDzyYtjXU5GhGxJVHjRvGrSP_iYKnIQbq_MuVq86rSObCeJvo2iXFRUjLgs" \
            "U9wDzhqK9J_SHmpxDJHW_rBD8eilO26x2M_hzJfGB-V9cGF65GO_7CgJXI8Ktw188"
        image_url = "/some/image.jpg"

        expected_options = {
            'trim': 'trim', 'full': False, 'halign': 'center', 'fit_in': False,
            'vertical_flip': True, 'image': '/some/image.jpg',
            'crop': {'top': 11, 'right': 12, 'bottom': 13, 'left': 10},
            'height': 300, 'width': 300, 'meta': False, 'horizontal_flip': True,
            'filters': 'some_filter()', 'valign': 'middle', 'debug': False,
            'hash': 'e2baf424fa420b73a97476956dfb858f', 'adaptive': False, 'smart': True
        }
        options = self.cryptor.get_options(encrypted_str, image_url)
        expect(options).to_be_like(expected_options)

    def test_get_options_returns_null_if_invalid(self):
        encrypted_str = "hELdyDzyYtjXU5GhGxJVHjRvGrSP_iYKnIQbq_MuVq86rSObCeJvo2iXFRUjLgs"
        image_url = "/some/image.jpg"

        options = self.cryptor.get_options(encrypted_str, image_url)
        expect(options).to_be_null()

    def test_get_options_returns_null_if_different_path(self):
        encrypted_str = "hELdyDzyYtjXU5GhGxJVHjRvGrSP_iYKnIQbq_MuVq86rSObCeJvo2iXFRUjLgs" \
            "U9wDzhqK9J_SHmpxDJHW_rBD8eilO26x2M_hzJfGB-V9cGF65GO_7CgJXI8Ktw188"
        image_url = "/some/image2.jpg"

        options = self.cryptor.get_options(encrypted_str, image_url)
        expect(options).to_be_null()

    def test_get_options_from_storage(self):
        image_url = "/some/image.jpg"
        custom_security_key = "custom-sec"
        cryptor = Cryptor(security_key=custom_security_key)
        decryptor = Cryptor(security_key="something")

        expected_options = dict(
            width=300,
            height=300,
            smart=True,
            adaptive=False,
            full=False,
            fit_in=False,
            flip_horizontal=True,
            flip_vertical=True,
            halign="center",
            valign="middle",
            trim=True,
            crop_left=10,
            crop_top=11,
            crop_right=12,
            crop_bottom=13,
            filters='some_filter()',
            image=image_url,
        )

        encrypted_str = cryptor.encrypt(**expected_options)

        mock_storage = mock.Mock()
        decryptor.context = mock.Mock(
            config=mock.Mock(
                STORES_CRYPTO_KEY_FOR_EACH_IMAGE=True
            ),
            modules=mock.Mock(
                storage=mock_storage
            ),
        )

        mock_storage.get_crypto.return_value = custom_security_key

        options = decryptor.get_options(encrypted_str, image_url)
        expect(options).not_to_be_null()

        expected_options = {
            'trim': 'trim', 'full': False, 'halign': 'center', 'fit_in': False,
            'vertical_flip': True, 'image': '/some/image.jpg',
            'crop': {'top': 11, 'right': 12, 'bottom': 13, 'left': 10},
            'height': 300, 'width': 300, 'meta': False, 'horizontal_flip': True,
            'filters': 'some_filter()', 'valign': 'middle', 'debug': False,
            'hash': 'e2baf424fa420b73a97476956dfb858f', 'adaptive': False, 'smart': True
        }

        expect(options).to_be_like(expected_options)

    def test_get_options_from_storage_returns_null_if_key_not_found(self):
        image_url = "/some/image.jpg"
        custom_security_key = "custom-sec"
        cryptor = Cryptor(security_key=custom_security_key)
        decryptor = Cryptor(security_key="something")

        expected_options = dict(
            width=300,
            height=300,
            smart=True,
            adaptive=False,
            full=False,
            fit_in=False,
            flip_horizontal=True,
            flip_vertical=True,
            halign="center",
            valign="middle",
            trim=True,
            crop_left=10,
            crop_top=11,
            crop_right=12,
            crop_bottom=13,
            filters='some_filter()',
            image=image_url,
        )

        encrypted_str = cryptor.encrypt(**expected_options)

        mock_storage = mock.Mock()
        decryptor.context = mock.Mock(
            config=mock.Mock(
                STORES_CRYPTO_KEY_FOR_EACH_IMAGE=True
            ),
            modules=mock.Mock(
                storage=mock_storage
            ),
        )

        mock_storage.get_crypto.return_value = None

        options = decryptor.get_options(encrypted_str, image_url)
        expect(options).to_be_null()


def test_decrypting_combinations():
    cryptor = Cryptor('my-security-key')
    for test in DECRYPT_TESTS:
        base_copy = copy.copy(BASE_PARAMS)
        base_copy.update(test['params'])
        encrypted = cryptor.encrypt(**base_copy)
        yield decrypted_result_should_match, cryptor.decrypt(encrypted), test['result']


def decrypted_result_should_match(decrypted, expected):
    expect(decrypted).to_be_like(expected)
