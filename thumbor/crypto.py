#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import base64
import hashlib

from Crypto.Cipher import AES

# Import the Signer class to support backward-compatibility
# and existing documentation
from thumbor.url_signers.base64_hmac_sha1 import UrlSigner as Signer  # NOQA
from thumbor.url import Url


class Cryptor(object):
    def __init__(self, security_key):
        self.security_key = (security_key * 16)[:16]

    def encrypt(self,
                width,
                height,
                smart,
                adaptive,
                full,
                fit_in,
                flip_horizontal,
                flip_vertical,
                halign,
                valign,
                trim,
                crop_left,
                crop_top,
                crop_right,
                crop_bottom,
                filters,
                image):

        generated_url = Url.generate_options(
            width=width,
            height=height,
            smart=smart,
            meta=False,
            adaptive=adaptive,
            full=full,
            fit_in=fit_in,
            horizontal_flip=flip_horizontal,
            vertical_flip=flip_vertical,
            halign=halign,
            valign=valign,
            trim=trim,
            crop_left=crop_left,
            crop_top=crop_top,
            crop_right=crop_right,
            crop_bottom=crop_bottom,
            filters=filters
        )

        url = "%s/%s" % (generated_url, hashlib.md5(image).hexdigest())

        def pad(s):
            return s + (16 - len(s) % 16) * "{"

        cipher = AES.new(self.security_key)
        encrypted = base64.urlsafe_b64encode(cipher.encrypt(pad(url.encode('utf-8'))))

        return encrypted

    def try_decrypt(self, encrypted_url_part, cryptor=None):
        decryptor = self
        if cryptor is not None:
            decryptor = cryptor

        try:
            opt = decryptor.decrypt(encrypted_url_part)
            if opt is not None:
                unicode(opt['image_hash'])
        except (UnicodeDecodeError, ValueError):
            opt = None

        return opt

    def get_options(self, encrypted_url_part, image_url):
        opt = self.try_decrypt(encrypted_url_part)

        # why this check for not self.security_key???
        # if opt is None and not self.security_key and self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
        if opt is None and self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            security_key = self.context.modules.storage.get_crypto(image_url)

            if security_key is not None:
                cr = Cryptor(security_key)
                opt = self.try_decrypt(encrypted_url_part, cryptor=cr)

        if opt is None:
            return None

        image_hash = opt and opt.get('image_hash')
        image_hash = image_hash[1:] if image_hash and image_hash.startswith('/') else image_hash

        path_hash = hashlib.md5(image_url.encode('utf-8')).hexdigest()

        if not image_hash or image_hash != path_hash:
            return None

        opt['image'] = image_url
        opt['hash'] = opt['image_hash']
        del opt['image_hash']

        return opt

    def decrypt(self, encrypted):
        cipher = AES.new(self.security_key)

        try:
            debased = base64.urlsafe_b64decode(encrypted.encode("utf-8"))
            decrypted = cipher.decrypt(debased).rstrip('{')
        except TypeError:
            return None

        result = Url.parse_decrypted('/%s' % decrypted)

        result['image_hash'] = result['image']
        del result['image']

        return result
