#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import base64
import hashlib
import urlparse

from Crypto.Cipher import *

from thumbor.url import Url

class Crypto(object):
    def __init__(self, salt):
        self.salt = (salt * 16)[:16]

    def encrypt(self, 
                width,
                height,
                smart,
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
        encrypted = base64.urlsafe_b64encode(cipher.encrypt(pad(url)))

        return encrypted

    def decrypt(self, encrypted):
        cipher = AES.new(self.salt)

        debased = base64.urlsafe_b64decode(encrypted)
        decrypted = cipher.decrypt(debased).rstrip('{')

        if not decrypted or not urlparse.urlparse(decrypted):
            return None

        result = Url.parse('/%s' % decrypted, with_unsafe=False)
        if not result:
            return None

        result['image_hash'] = result['image']
        del result['image']

        return result

