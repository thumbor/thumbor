#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.loaders import http_loader
from tornado.concurrent import return_future


def _normalize_url(url):
    url = http_loader.quote_url(url)
    if url.startswith('http:'):
        url = url.replace('http:', 'https:', 1)

    return url if url.startswith('https://') else 'https://%s' % url


def validate(context, url):
    if url.startswith('http://'):
        return False

    return http_loader.validate(context, url, normalize_url_func=_normalize_url)


def return_contents(response, url, callback, context):
    return http_loader.return_contents(response, url, callback, context)


@return_future
def load(context, url, callback):
    return http_loader.load_sync(context, url, callback, normalize_url_func=_normalize_url)


def encode(string):
    return http_loader.encode(string)
