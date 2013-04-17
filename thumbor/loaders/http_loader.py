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

http_client = None


def _normalize_url(url):
    return url if url.startswith('http') else 'http://%s' % url


def validate(context, url):
    url = _normalize_url(url)
    res = urlparse(url)

    if not res.hostname:
        return False

    if not context.config.ALLOWED_SOURCES:
        return True

    for pattern in context.config.ALLOWED_SOURCES:
        if re.match('^%s$' % pattern, res.hostname):
            return True

    return False


def return_contents(response, url, callback):
    if response.error:
        logger.error("ERROR retrieving image {0}: {1}".format(url, str(response.error)))
        callback(None)
    elif response.body is None or len(response.body) == 0:
        logger.error("ERROR retrieving image {0}: Empty response.".format(url))
        callback(None)
    else:
        callback(response.body)


def load(context, url, callback):
    client = http_client
    if client is None:
        client = tornado.httpclient.AsyncHTTPClient()

    url = _normalize_url(url)
    client.fetch(url, callback=partial(return_contents, url=url, callback=callback))
