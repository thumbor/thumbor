#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import datetime
import re
import socket
from typing import Pattern
from urllib.parse import quote, unquote, urlparse

import tornado.httpclient

from thumbor.loaders import LoaderResult
from thumbor.utils import logger

try:
    import tornado.curl_httpclient  # pylint: disable=ungrouped-imports
except (ImportError, ValueError):
    logger.warning(
        "pycurl usage is advised. It could not be loaded properly. Verify install..."
    )


def encode_url(url):
    if url == unquote(url):
        return quote(url, safe="~@#$&()*!+=:;,.?/'")

    return url


def encode(string):
    return None if string is None else string.encode("ascii")


def quote_url(url):
    return encode_url(unquote(url))


def _normalize_url(url):
    url = quote_url(url)
    return url if url.startswith("http") else f"http://{url}"


def validate(context, url, normalize_url_func=_normalize_url):
    url = normalize_url_func(url)
    res = urlparse(url)

    if not res.hostname:
        return False

    if not context.config.ALLOWED_SOURCES:
        return True

    for pattern in context.config.ALLOWED_SOURCES:
        if isinstance(  # pylint: disable=isinstance-second-argument-not-valid-type
            pattern, Pattern
        ):
            match = url
        else:
            pattern = f"^{pattern}$"
            match = res.hostname

        if re.match(pattern, match):
            return True

    return False


def return_contents(response, url, context, req_start=None):
    res = urlparse(url)
    netloc = res.netloc.replace(".", "_")
    code = response.code

    if req_start:
        finish = datetime.datetime.now()
        context.metrics.timing(
            f"original_image.fetch.{code}.{netloc}",
            (finish - req_start).total_seconds() * 1000,
        )
        context.metrics.incr(
            f"original_image.fetch.{code}.{netloc}",
        )

    result = LoaderResult()
    context.metrics.incr(f"original_image.status.{code}")
    context.metrics.incr(f"original_image.status.{code}.{netloc}")
    if response.error:
        result.successful = False
        if response.code == 599:
            # Return a Gateway Timeout status downstream if upstream times out
            result.error = LoaderResult.ERROR_TIMEOUT
        else:
            result.error = LoaderResult.ERROR_NOT_FOUND

        logger.warning(
            "ERROR retrieving image %s: %s", url, str(response.error)
        )

    elif response.body is None or len(response.body) == 0:
        result.successful = False
        result.error = LoaderResult.ERROR_UPSTREAM

        logger.warning("ERROR retrieving image %s: Empty response.", url)
    else:
        if response.time_info:
            for metric_name in response.time_info:
                context.metrics.timing(
                    "original_image.time_info." + metric_name,
                    response.time_info[metric_name] * 1000,
                )
            context.metrics.timing(
                "original_image.time_info.bytes_per_second",
                len(response.body) // response.time_info["total"],
            )
        result.buffer = response.body
        result.metadata.update(response.headers)
        context.metrics.incr(
            "original_image.response_bytes", len(response.body)
        )

    return result


async def load(
    context,
    url,
    normalize_url_func=_normalize_url,
    return_contents_fn=return_contents,
    encode_fn=encode,
):
    using_proxy = (
        context.config.HTTP_LOADER_PROXY_HOST
        and context.config.HTTP_LOADER_PROXY_PORT
    )
    if using_proxy or context.config.HTTP_LOADER_CURL_ASYNC_HTTP_CLIENT:
        http_client_implementation = (
            "tornado.curl_httpclient.CurlAsyncHTTPClient"
        )
        prepare_curl_callback = _get_prepare_curl_callback(context.config)
    else:
        http_client_implementation = None  # default
        prepare_curl_callback = None

    tornado.httpclient.AsyncHTTPClient.configure(
        http_client_implementation,
        max_clients=context.config.HTTP_LOADER_MAX_CLIENTS,
    )
    client = tornado.httpclient.AsyncHTTPClient()

    user_agent = None
    headers = {"Accept": "image/*;q=0.9,*/*;q=0.1"}
    if context.config.HTTP_LOADER_FORWARD_ALL_HEADERS:
        headers = context.request_handler.request.headers
    else:
        if context.config.HTTP_LOADER_FORWARD_USER_AGENT:
            if "User-Agent" in context.request_handler.request.headers:
                user_agent = context.request_handler.request.headers[
                    "User-Agent"
                ]
        if context.config.HTTP_LOADER_FORWARD_HEADERS_WHITELIST:
            for (
                header_key
            ) in context.config.HTTP_LOADER_FORWARD_HEADERS_WHITELIST:
                if header_key in context.request_handler.request.headers:
                    headers[header_key] = (
                        context.request_handler.request.headers[header_key]
                    )

    if user_agent is None and "User-Agent" not in headers:
        user_agent = context.config.HTTP_LOADER_DEFAULT_USER_AGENT

    url = normalize_url_func(url)
    req = tornado.httpclient.HTTPRequest(
        url=url,
        headers=headers,
        connect_timeout=context.config.HTTP_LOADER_CONNECT_TIMEOUT,
        request_timeout=context.config.HTTP_LOADER_REQUEST_TIMEOUT,
        follow_redirects=context.config.HTTP_LOADER_FOLLOW_REDIRECTS,
        max_redirects=context.config.HTTP_LOADER_MAX_REDIRECTS,
        user_agent=user_agent,
        proxy_host=encode_fn(context.config.HTTP_LOADER_PROXY_HOST),
        proxy_port=context.config.HTTP_LOADER_PROXY_PORT,
        proxy_username=encode_fn(context.config.HTTP_LOADER_PROXY_USERNAME),
        proxy_password=encode_fn(context.config.HTTP_LOADER_PROXY_PASSWORD),
        ca_certs=encode_fn(context.config.HTTP_LOADER_CA_CERTS),
        client_key=encode_fn(context.config.HTTP_LOADER_CLIENT_KEY),
        client_cert=encode_fn(context.config.HTTP_LOADER_CLIENT_CERT),
        validate_cert=context.config.HTTP_LOADER_VALIDATE_CERTS,
        prepare_curl_callback=prepare_curl_callback,
    )

    start = datetime.datetime.now()
    try:
        response = await client.fetch(req, raise_error=True)
    except tornado.httpclient.HTTPClientError as err:
        response = tornado.httpclient.HTTPResponse(
            req, err.code, reason=err.message, start_time=start
        )
    except socket.gaierror as err:
        response = tornado.httpclient.HTTPResponse(
            req, 599, reason=str(err), start_time=start
        )

    return return_contents_fn(
        response=response,
        url=url,
        context=context,
        req_start=start,
    )


def _get_prepare_curl_callback(config):
    if (
        config.HTTP_LOADER_CURL_LOW_SPEED_TIME == 0
        or config.HTTP_LOADER_CURL_LOW_SPEED_LIMIT == 0
    ):
        return None

    class CurlOpts:
        def __init__(self, config):
            self.config = config

        def prepare_curl_callback(self, curl):
            curl.setopt(
                curl.LOW_SPEED_TIME,
                self.config.HTTP_LOADER_CURL_LOW_SPEED_TIME,
            )
            curl.setopt(
                curl.LOW_SPEED_LIMIT,
                self.config.HTTP_LOADER_CURL_LOW_SPEED_LIMIT,
            )

    return CurlOpts(config).prepare_curl_callback
