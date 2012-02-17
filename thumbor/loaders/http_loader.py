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

http_client = None

def _normalize_url(url):
    return url if url.startswith('http') else 'http://%s' % url

def validate(context, url):
    if not context.config.ALLOWED_SOURCES:
        return True

    url = _normalize_url(url)
    res = urlparse(url)
    for pattern in context.config.ALLOWED_SOURCES:
        if re.match('^%s$' % pattern, res.hostname):
            return True
    return False

def return_contents(response, callback):
    if response.error or not response.headers['Content-Type'][:6] == 'image/' or len(response.body) == 0:
        callback(None)
    else:
        callback(response.body)

def load(context, url, callback):
    client = http_client
    if client is None:
        client = tornado.httpclient.AsyncHTTPClient()

    url = _normalize_url(url)
    client.fetch(url, callback=partial(return_contents, callback=callback))

