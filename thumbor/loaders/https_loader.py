#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.loaders import http_loader
from tornado import gen


def _normalize_url(url):
    url = http_loader.quote_url(url)
    return url if url.startswith('http') else 'https://%s' % url


def validate(context, url):
    return http_loader.validate(context, url, normalize_url_func=_normalize_url)


def return_contents(response, url, context):
    return http_loader.return_contents(response, url, context)


@gen.coroutine
def load(context, url):
    result = yield http_loader.load(context, url, normalize_url_func=_normalize_url)
    raise gen.Return(result)


def encode(string):
    return http_loader.encode(string)
