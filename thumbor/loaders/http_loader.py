#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import re
from functools import partial
from urllib import unquote, quote
from urlparse import urlparse

import tornado.httpclient

from . import LoaderResult
from thumbor.media import Media
from thumbor.utils import logger
from tornado.concurrent import return_future

QUOTE_PATH_REGEX = re.compile(r"((?:https?:\/\/)?[^/]+)(\/.*)")


def quote_url(url):
    try:
        url = url.encode('utf-8')
    except UnicodeDecodeError:
        pass

    url = QUOTE_PATH_REGEX.split(url)
    if len(url) > 2:
        url[2] = quote(url[2])
    url = ''.join(url)
    return url


def _normalize_url(url):
    url = quote_url(unquote(url))
    return url if url.startswith('http') else 'http://%s' % url


def validate(context, url, normalize_url_func=_normalize_url):
    url = normalize_url_func(url)
    res = urlparse(url)

    if not res.hostname:
        return False

    if not context.config.ALLOWED_SOURCES:
        return True

    for pattern in context.config.ALLOWED_SOURCES:
        if re.match('^%s$' % pattern, res.hostname):
            return True

    return False


def return_contents(response, url, callback, context):

    media = Media()

    context.metrics.incr('original_image.status.' + str(response.code))
    if response.error:
        media.is_valid = False

        if response.code == 599:
            # Return a Gateway Timeout status downstream if upstream times out
            media.errors.append(LoaderResult.ERROR_TIMEOUT)
        else:
            media.errors.append(LoaderResult.ERROR_NOT_FOUND)

        logger.warn("ERROR retrieving image {0}: {1}".format(url, str(response.error)))

    elif response.body is None or len(response.body) == 0:
        media.is_valid = False
        media.errors.append(LoaderResult.ERROR_UPSTREAM)

        logger.warn("ERROR retrieving image {0}: Empty response.".format(url))
    else:
        if response.time_info:
            for x in response.time_info:
                context.metrics.timing('original_image.time_info.' + x, response.time_info[x] * 1000)
            context.metrics.timing('original_image.time_info.bytes_per_second', len(response.body) / response.time_info['total'])

        media.buffer = response.body

    callback(media)


@return_future
def load(context, url, callback, normalize_url_func=_normalize_url):
    load_sync(context, url, callback, normalize_url_func)


def load_sync(context, url, callback, normalize_url_func):
    using_proxy = context.config.HTTP_LOADER_PROXY_HOST and context.config.HTTP_LOADER_PROXY_PORT
    if using_proxy or context.config.HTTP_LOADER_CURL_ASYNC_HTTP_CLIENT:
        tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

    client = tornado.httpclient.AsyncHTTPClient(max_clients=context.config.HTTP_LOADER_MAX_CLIENTS)

    user_agent = None
    if context.config.HTTP_LOADER_FORWARD_USER_AGENT:
        if 'User-Agent' in context.request_handler.request.headers:
            user_agent = context.request_handler.request.headers['User-Agent']

    if user_agent is None:
        user_agent = context.config.HTTP_LOADER_DEFAULT_USER_AGENT

    url = normalize_url_func(url)
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
        proxy_password=encode(context.config.HTTP_LOADER_PROXY_PASSWORD),
        ca_certs=encode(context.config.HTTP_LOADER_CA_CERTS),
        client_key=encode(context.config.HTTP_LOADER_CLIENT_KEY),
        client_cert=encode(context.config.HTTP_LOADER_CLIENT_CERT)
    )

    client.fetch(req, callback=partial(return_contents, url=url, callback=callback, context=context))


def encode(string):
    return None if string is None else string.encode('ascii')
