#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import re
from urlparse import urlparse
from functools import partial

import tornado.httpclient

from thumbor.utils import logger
from thumbor.loaders import http_loader
from tornado.concurrent import return_future


def _normalize_url(url):
    return url if url.startswith('https') else 'https://%s' % url


def validate(context, url):
    url = _normalize_url(url)
    res = urlparse(url)

    if not url.startswith('https'):
        return False

    if not res.hostname:
        return False

    if not context.config.ALLOWED_SOURCES:
        return True

    for pattern in context.config.ALLOWED_SOURCES:
        if re.match('^%s$' % pattern, res.hostname):
            return True

    return False


def return_contents(response, url, callback, context):
    return http_loader.return_contents(response, url, callback, context)


@return_future
def load(context, url, callback):
    return http_loader.load(context, url, callback, normalize_url_func=_normalize_url)


def encode(string):
    return http_loader.encode(string)
