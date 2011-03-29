#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import base64

from pyDes import *

class Crypto(object):
    def __init__(self, salt):
        self.salt = (salt * 24)[:24]

    def __form_url(self, width, height, smart):
        url = [
            '%sx%s' % (width, height)
        ]

        if smart:
            url.append("smart")

        return "/".join(url)

    def __deform_url(self, url):
        reg = "(\d+)x(\d+)/?(smart)?"
        res = re.match(reg, url)
        groups = res.groups()

        result = {
            "width": int(groups[0]),
            "height": int(groups[1])
        }

        result['smart'] = groups[2] == "smart"

        return result

    def encrypt(self, width, height, smart):

        url = self.__form_url(width, height, smart)

        key = triple_des(self.salt,
                         CBC, 
                         '\0\0\0\0\0\0\0\0', 
                         pad=None, 
                         padmode=PAD_PKCS5)

        return base64.urlsafe_b64encode(key.encrypt(url))

    def decrypt(self, encrypted):

        key = triple_des(self.salt,
                         CBC, 
                         '\0\0\0\0\0\0\0\0', 
                         pad=None, 
                         padmode=PAD_PKCS5)

        decrypted = key.decrypt(base64.urlsafe_b64decode(encrypted))

        if not decrypted:
            return None

        return self.__deform_url(decrypted)

