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
    # using_proxy = context.config.HTTP_LOADER_PROXY_HOST and context.config.HTTP_LOADER_PROXY_PORT
    # if using_proxy or context.config.HTTP_LOADER_CURL_ASYNC_HTTP_CLIENT:
        # http_client_implementation = 'tornado.curl_httpclient.CurlAsyncHTTPClient'
        # prepare_curl_callback = _get_prepare_curl_callback(context.config)
    # else:
        # http_client_implementation = None  # default
        # prepare_curl_callback = None

    # http_client_implementation = None  # default
    # prepare_curl_callback = None

    # tornado.httpclient.AsyncHTTPClient.configure(http_client_implementation, max_clients=context.config.HTTP_LOADER_MAX_CLIENTS)
    # tornado.httpclient.AsyncHTTPClient.configure(http_client_implementation, max_clients=10)
    client = tornado.httpclient.AsyncHTTPClient()

    # user_agent = None
    headers = {}
    # if context.config.HTTP_LOADER_FORWARD_ALL_HEADERS:
        # headers = context.request_handler.request.headers
    # else:
        # if context.config.HTTP_LOADER_FORWARD_USER_AGENT:
            # if 'User-Agent' in context.request_handler.request.headers:
                # user_agent = context.request_handler.request.headers['User-Agent']
        # if context.config.HTTP_LOADER_FORWARD_HEADERS_WHITELIST:
            # for header_key in context.config.HTTP_LOADER_FORWARD_HEADERS_WHITELIST:
                # if header_key in context.request_handler.request.headers:
                    # headers[header_key] = context.request_handler.request.headers[header_key]

    # if user_agent is None and 'User-Agent' not in headers:
        # user_agent = context.config.HTTP_LOADER_DEFAULT_USER_AGENT
    # headers = request.headers

    # url = _normalize_url(request_parameters.image_url)
    url = request_parameters.image_url
    image_request = tornado.httpclient.HTTPRequest(
        url=url,
        headers=headers,
        # connect_timeout=10,
        # request_timeout=10,
        # follow_redirects=True,
        # max_redirects=3,
        # user_agent=user_agent,
        # proxy_host=encode(context.config.HTTP_LOADER_PROXY_HOST),
        # proxy_port=context.config.HTTP_LOADER_PROXY_PORT,
        # proxy_username=encode(context.config.HTTP_LOADER_PROXY_USERNAME),
        # proxy_password=encode(context.config.HTTP_LOADER_PROXY_PASSWORD),
        # ca_certs=encode(context.config.HTTP_LOADER_CA_CERTS),
        # client_key=encode(context.config.HTTP_LOADER_CLIENT_KEY),
        # client_cert=encode(context.config.HTTP_LOADER_CLIENT_CERT),
        # validate_cert=context.config.HTTP_LOADER_VALIDATE_CERTS,
        # prepare_curl_callback=prepare_curl_callback
    )

    # start = datetime.datetime.now()
    response = yield client.fetch(image_request, raise_error=False)

    if response.code > 399:
        details.status_code = response.code
        details.finish_early = True
        details.body = "Could not load source image: %d (%s)" % (response.code, response.body)
        return

    details.source_image = response.buffer.read()
