#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import os
from os.path import exists
import copy
import inspect

from thumbor.crypto import Cryptor, Signer
from thumbor.url import Url


class BaseStorage(object):
    def __init__(self, context):
        self.context = context

    def put(self, bytes):
        raise NotImplementedError()

    def get(self):
        raise NotImplementedError()

    def remove(self):
        raise NotImplementedError()

    def ensure_dir(self, path):
        if not exists(path):
            try:
                os.makedirs(path)
            except OSError, err:
                # FILE ALREADY EXISTS = 17
                if err.errno != 17:
                    raise

    def path_without_remove(self):
        params = copy.copy(vars(self.context.request))
        param_keys = set(params.keys())

        url_generate_keywords = inspect.getargspec(Url.generate_options).args
        url_generate_keywords.remove('cls')
        url_generate_keywords = set(url_generate_keywords)
        for keyword in (param_keys - url_generate_keywords):
          del params[keyword]
        params['purge'] = False

        signer = Signer(self.context.server._security_key)
        url = Url.generate_options(**params)
        url = '%s/%s' % (url, self.context.request.image_url)
        url = url.lstrip('/')

        signature = signer.signature(url)

        path = '/%s/%s' % (signature, url)
        return path
