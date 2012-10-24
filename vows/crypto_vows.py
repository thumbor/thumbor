#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import hashlib
import base64
import hmac
import copy

from pyvows import Vows, expect

from thumbor.crypto import Cryptor, Signer

@Vows.batch
class CryptoVows(Vows.Context):
    def topic(self):
        return Cryptor(security_key="something")

    def should_be_crypto_instance(self, topic):
        expect(topic).to_be_instance_of(Cryptor)

    def should_calculate_salt(self, topic):
        expect(topic.security_key).to_equal('somethingsomethi')

    class DecryptInvalidString(Vows.Context):

        def topic(self, crypto):
            return crypto.decrypt('some string')

        def should_be_null(self, topic):
            expect(topic).to_be_null()

    class Encrypt(Vows.Context):
        def topic(self, crypto):
            return crypto.encrypt(width=300,
                                  height=300,
                                  smart=True,
                                  adaptive=False,
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
                                  image="/some/image.jpg")

        def should_equal_encrypted_string(self, topic):
            encrypted_str = "hELdyDzyYtjXU5GhGxJVHjRvGrSP_iYKnIQbq_MuVq86rSObCeJvo2iXFRUjLgsU9wDzhqK9J_SHmpxDJHW_rBD8eilO26x2M_hzJfGB-V9cGF65GO_7CgJXI8Ktw188"
            expect(topic).to_equal(encrypted_str)

        class Decrypt(Vows.Context):

            def topic(self, encrypted, crypto):
                return crypto.decrypt(encrypted)

            def should_not_be_an_error(self, topic):
                expect(topic).not_to_be_an_error()

            def should_not_be_an_empty_dict(self, topic):
                expect(topic).not_to_be_empty()

            def should_have_300_of_width(self, topic):
                expect(topic['width']).to_equal(300)

            def should_have_200_of_height(self, topic):
                expect(topic['height']).to_equal(300)

            def should_have_smart_flag(self, topic):
                expect(topic['smart']).to_be_true()

            def should_not_have_fitin_flag(self, topic):
                expect(topic['fit_in']).to_be_false()

            def should_have_flip_horizontal_flag(self, topic):
                expect(topic['horizontal_flip']).to_be_true()

            def should_have_flip_vertical_flag(self, topic):
                expect(topic['vertical_flip']).to_be_true()

            def should_have_center_halign(self, topic):
                expect(topic['halign']).to_equal('center')

            def should_have_middle_valign(self, topic):
                expect(topic['valign']).to_equal('middle')

            def should_have_crop_left_of_10(self, topic):
                expect(topic['crop']['left']).to_equal(10)

            def should_have_crop_top_of_11(self, topic):
                expect(topic['crop']['top']).to_equal(11)

            def should_have_crop_right_of_12(self, topic):
                expect(topic['crop']['right']).to_equal(12)

            def should_have_crop_bottom_of_13(self, topic):
                expect(topic['crop']['bottom']).to_equal(13)

            def should_have_filter_as_some_filter(self, topic):
                expect(topic['filters']).to_equal('some_filter()')

            def should_have_image_hash(self, topic):
                image_hash = hashlib.md5('/some/image.jpg').hexdigest()
                expect(topic['image_hash']).to_equal(image_hash)

        class DecryptWrongKey(Vows.Context):

            def topic(self, encrypted, crypto):
                crypto2 = Cryptor(security_key="simething")

                return (crypto2.decrypt(encrypted), crypto.decrypt(encrypted))

            def should_return_empty(self, topic):
                wrong, right = topic
                expect(wrong['image_hash']).not_to_equal(right['image_hash'])


@Vows.batch
class SignerVows(Vows.Context):
    def topic(self):
        return Signer(security_key="something")

    def should_be_signer_instance(self, topic):
        expect(topic).to_be_instance_of(Signer)

    def should_have_security_key(self, topic):
        expect(topic.security_key).to_equal('something')

    class Sign(Vows.Context):
        def topic(self, signer):
            url = '10x11:12x13/-300x-300/center/middle/smart/some/image.jpg'
            expected = base64.urlsafe_b64encode(hmac.new('something', unicode(url).encode('utf-8'), hashlib.sha1).digest())
            return (signer.signature(url), expected)

        def should_equal_encrypted_string(self, (topic, expected)):
            expect(topic).to_equal(expected)


BASE_IMAGE_URL = 'my.domain.com/some/image/url.jpg'
BASE_IMAGE_MD5 = 'f33af67e41168e80fcc5b00f8bd8061a'

BASE_PARAMS = {
    'width': 0,
    'height': 0,
    'smart': False,
    'adaptive': False,
    'fit_in': False,
    'flip_horizontal': False,
    'flip_vertical': False,
    'halign': 'center',
    'valign': 'middle',
    'trim': '',
    'crop_left': 0,
    'crop_top': 0,
    'crop_right': 0,
    'crop_bottom': 0,
    'filters': '',
    'image': ''
}

DECRYPT_TESTS = [
    {
        'params': {
            'width': 300, 'height': 200, 'image': BASE_IMAGE_URL
        },
        'result': {
            "horizontal_flip": False,
            "vertical_flip": False,
            "smart": False,
            "meta": False,
            "fit_in": False,
            "crop": {
                "left": 0,
                "top": 0,
                "right": 0,
                "bottom": 0
            },
            "valign": 'middle',
            "halign": 'center',
            "image_hash": BASE_IMAGE_MD5,
            "width": 300,
            "height": 200,
            'filters': '',
            'debug': False,
            'adaptive': False,
            'trim': None
        }
    },
    {
        'params': {
            'filters': "quality(20):brightness(10)",
            'image': BASE_IMAGE_URL
        },
        'result': {
            "horizontal_flip": False,
            "vertical_flip": False,
            "smart": False,
            "meta": False,
            "fit_in": False,
            "crop": {
                "left": 0,
                "top": 0,
                "right": 0,
                "bottom": 0
            },
            "valign": 'middle',
            "halign": 'center',
            "image_hash": BASE_IMAGE_MD5,
            "width": 0,
            "height": 0,
            'filters': 'quality(20):brightness(10)',
            'debug': False,
            'adaptive': False,
            'trim': None
        }
    }
]

@Vows.batch
class CryptoDecryptVows(Vows.Context):
    def topic(self):
        cryptor = Cryptor('my-security-key')
        for test in DECRYPT_TESTS:
            base_copy = copy.copy(BASE_PARAMS)
            base_copy.update(test['params'])
            encrypted = cryptor.encrypt(**base_copy)
            yield(cryptor.decrypt(encrypted), test['result'])

    def decrypted_result_should_match(self, (decrypted, expected)):
        expect(decrypted).to_be_like(expected)
