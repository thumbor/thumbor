#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import logging
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
    if response.error:
        logging.error("ERROR retrieving image {0}: {1}".format(response.effective_url, str(response.error)))
        callback(None)
    elif not response.headers['Content-Type'][:5] == 'image':
        logging.error("ERROR retrieving image {0}: Expected response type starting with 'image', found {1}".format(response.effective_url, response.headers['Content-Type']))
        callback(None)
    elif len(response.body) == 0:
        logging.error("ERROR retrieving image {0}: Empty response.".format(response.effective_url))
        callback(None)
    else:
        callback(response.body)

def load(context, url, callback):
    client = http_client
    if client is None:
        client = tornado.httpclient.AsyncHTTPClient()

    url = _normalize_url(url)
    client.fetch(url, callback=partial(return_contents, callback=callback))

