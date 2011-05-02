#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import hashlib

from pyvows import Vows, expect

from thumbor.crypto import Crypto

@Vows.batch
class CryptoVows(Vows.Context):
    def topic(self):
        return Crypto(salt="something")

    def should_be_crypto_instance(self, topic):
        expect(topic).to_be_instance_of(Crypto)

    def should_calculate_salt(self, topic):
        expect(topic.salt).to_equal('somethingsomethi')

    class DecryptInvalidString(Vows.Context):

        def topic(self, crypto):
            return crypto.decrypt('some string')

        def should_be_null(self, topic):
            expect(topic).not_to_be_null()

    class Encrypt(Vows.Context):
        def topic(self, crypto):
            return crypto.encrypt(width=300,
                                  height=300,
                                  smart=True,
                                  fit_in=False,
                                  flip_horizontal=True,
                                  flip_vertical=True,
                                  halign="center",
                                  valign="middle",
                                  crop_left=10,
                                  crop_top=11,
                                  crop_right=12,
                                  crop_bottom=13,
                                  image="/some/image.jpg")

        def should_equal_encrypted_string(self, topic):
            encrypted_str = "OI8j7z9h88_IVzYLiq9UWPkBPBwwJ1pMKQw1UVrL7odTcog5UT4PBBrzoehKm7WUNxU5oq8mV59xMJJUc2aKWA=="
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

            def should_have_image_hash(self, topic):
                image_hash = hashlib.md5('/some/image.jpg').hexdigest()
                expect(topic['image_hash']).to_equal(image_hash)

        class DecryptWrongKey(Vows.Context):

            def topic(self, encrypted, crypto):
                crypto2 = Crypto(salt="simething")

                return (crypto2.decrypt(encrypted), crypto.decrypt(encrypted))

            def should_return_empty(self, topic):
                wrong, right = topic
                expect(wrong['image_hash']).not_to_equal(right['image_hash'])


