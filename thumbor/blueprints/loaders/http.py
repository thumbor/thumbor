#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import tornado.gen

from thumbor.lifecycle import Events


def plug_into_lifecycle():
    Events.subscribe(Events.Imaging.load_source_image, on_load_source_image)


@tornado.gen.coroutine
def on_load_source_image(sender, request, details):
    request_parameters = details.request_parameters

    http_client_implementation = None  # default
    prepare_curl_callback = None

    using_proxy = details.config.HTTP_LOADER_PROXY_HOST and details.config.HTTP_LOADER_PROXY_PORT
    if using_proxy or details.config.HTTP_LOADER_CURL_ASYNC_HTTP_CLIENT:
        http_client_implementation = 'tornado.curl_httpclient.CurlAsyncHTTPClient'
        prepare_curl_callback = _get_prepare_curl_callback(details.config)
    else:
        http_client_implementation = None  # default
        prepare_curl_callback = None

    tornado.httpclient.AsyncHTTPClient.configure(http_client_implementation, max_clients=details.config.HTTP_LOADER_MAX_CLIENTS)
    client = tornado.httpclient.AsyncHTTPClient()

    user_agent = None
    headers = {}
    if details.config.HTTP_LOADER_FORWARD_ALL_HEADERS:
        headers = request.headers
    else:
        if details.config.HTTP_LOADER_FORWARD_USER_AGENT:
            if 'User-Agent' in request.headers:
                user_agent = request.headers['User-Agent']
        if details.config.HTTP_LOADER_FORWARD_HEADERS_WHITELIST:
            for header_key in details.config.HTTP_LOADER_FORWARD_HEADERS_WHITELIST:
                if header_key in request.headers:
                    headers[header_key] = request.headers[header_key]

    if user_agent is None and 'User-Agent' not in headers:
        user_agent = details.config.HTTP_LOADER_DEFAULT_USER_AGENT

    # url = _normalize_url(request_parameters.image_url)
    url = request_parameters.image_url
    image_request = tornado.httpclient.HTTPRequest(
        url=url,
        headers=headers,
        connect_timeout=details.config.HTTP_LOADER_CONNECT_TIMEOUT,
        request_timeout=details.config.HTTP_LOADER_REQUEST_TIMEOUT,
        follow_redirects=details.config.HTTP_LOADER_FOLLOW_REDIRECTS,
        max_redirects=details.config.HTTP_LOADER_MAX_REDIRECTS,
        user_agent=user_agent,
        proxy_host=_encode(details.config.HTTP_LOADER_PROXY_HOST),
        proxy_port=details.config.HTTP_LOADER_PROXY_PORT,
        proxy_username=_encode(details.config.HTTP_LOADER_PROXY_USERNAME),
        proxy_password=_encode(details.config.HTTP_LOADER_PROXY_PASSWORD),
        ca_certs=_encode(details.config.HTTP_LOADER_CA_CERTS),
        client_key=_encode(details.config.HTTP_LOADER_CLIENT_KEY),
        client_cert=_encode(details.config.HTTP_LOADER_CLIENT_CERT),
        validate_cert=details.config.HTTP_LOADER_VALIDATE_CERTS,
        prepare_curl_callback=prepare_curl_callback
    )

    # start = datetime.datetime.now()
    response = yield client.fetch(image_request, raise_error=False)

    if response.code > 399:
        details.status_code = response.code
        details.finish_early = True
        details.body = "Could not load source image: %d (%s)" % (response.code, response.body)
        return

    details.source_image = response.buffer.read()


def _encode(string):
    return None if string is None else string.encode('ascii')


def _get_prepare_curl_callback(config):
    if config.HTTP_LOADER_CURL_LOW_SPEED_TIME == 0 or config.HTTP_LOADER_CURL_LOW_SPEED_LIMIT == 0:
        return None

    class CurlOpts:
        def __init__(self, config):
            self.config = config

        def prepare_curl_callback(self, curl):
            curl.setopt(curl.LOW_SPEED_TIME, self.config.HTTP_LOADER_CURL_LOW_SPEED_TIME)
            curl.setopt(curl.LOW_SPEED_LIMIT, self.config.HTTP_LOADER_CURL_LOW_SPEED_LIMIT)

    return CurlOpts(config).prepare_curl_callback
