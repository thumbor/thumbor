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
        logger.warn("ERROR retrieving image {0}: {1}".format(url, str(response.error)))
        callback(None)
    elif response.body is None or len(response.body) == 0:
        logger.warn("ERROR retrieving image {0}: Empty response.".format(url))
        callback(None)
    else:
        callback(response.body)


def load(context, url, callback):
    client = http_client

    if client is None:
        if context.config.HTTP_LOADER_PROXY_HOST and context.config.HTTP_LOADER_PROXY_PORT:
            tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
        client = tornado.httpclient.AsyncHTTPClient()

    user_agent = None
    if context.config.HTTP_LOADER_FORWARD_USER_AGENT:
        if 'User-Agent' in context.request_handler.request.headers:
            user_agent = context.request_handler.request.headers['User-Agent']
    if user_agent is None:
        user_agent = context.config.HTTP_LOADER_DEFAULT_USER_AGENT

    url = _normalize_url(url)
    req = tornado.httpclient.HTTPRequest(
        url=encode(url),
        connect_timeout=context.config.HTTP_LOADER_CONNECT_TIMEOUT,
        request_timeout=context.config.HTTP_LOADER_REQUEST_TIMEOUT,
        follow_redirects=context.config.HTTP_LOADER_FOLLOW_REDIRECTS,
        max_redirects=context.config.HTTP_LOADER_MAX_REDIRECTS,
        user_agent=user_agent,
        proxy_host=encode(context.config.HTTP_LOADER_PROXY_HOST),
        proxy_port=context.config.HTTP_LOADER_PROXY_PORT,
        proxy_username=encode(context.config.HTTP_LOADER_PROXY_USERNAME),
        proxy_password=encode(context.config.HTTP_LOADER_PROXY_PASSWORD)
    )

    client.fetch(req, callback=partial(return_contents, url=url, callback=callback))

def encode(string):
    return None if string is None else string.encode('ascii')
