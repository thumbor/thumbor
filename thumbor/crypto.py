#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import base64
import hashlib

from Crypto.Cipher import AES

from thumbor.url import Url

class Crypto(object):
    def __init__(self, salt):
        self.salt = (salt * 16)[:16]

    def encrypt(self, 
                width,
                height,
                smart,
                fit_in,
                flip_horizontal,
                flip_vertical,
                halign,
                valign,
                crop_left,
                crop_top,
                crop_right,
                crop_bottom,
                image):

        url = "%s/%s" % (Url.generate_options(width,
                                              height,
                                              smart,
                                              False,
                                              fit_in,
                                              flip_horizontal,
                                              flip_vertical,
                                              halign,
                                              valign,
                                              crop_left,
                                              crop_top,
                                              crop_right,
                                              crop_bottom),
                        hashlib.md5(image).hexdigest())

        pad = lambda s: s + (16 - len(s) % 16) * "{"
        cipher = AES.new(self.salt)
        encrypted = base64.urlsafe_b64encode(cipher.encrypt(pad(url.encode('utf-8'))))

        return encrypted

    def decrypt(self, encrypted):
        cipher = AES.new(self.salt)

        debased = base64.urlsafe_b64decode(encrypted.encode("utf-8"))
        decrypted = cipher.decrypt(debased).rstrip('{')

        result = Url.parse('/%s' % decrypted, with_unsafe=False)

        result['image_hash'] = result['image']
        del result['image']

        return result

