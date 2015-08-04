# -*- coding: utf-8 -*-


class BaseUrlSigner(object):
    def __init__(self, security_key):
        if isinstance(security_key, unicode):
            security_key = security_key.encode('utf-8')
        self.security_key = security_key

    def validate(self, actual_signature, url):
        raise NotImplementedError()

    def signature(self, url):
        raise NotImplementedError()
