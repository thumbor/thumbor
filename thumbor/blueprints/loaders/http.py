#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import tornado.gen
import tornado.httpclient
from six.moves.urllib.parse import quote, unquote

from thumbor.blueprints.loaders import Loader as BaseLoader


def plug_into_lifecycle():
    HttpLoader()


class HttpLoader(BaseLoader):
    @classmethod
    @tornado.gen.coroutine
    def load_source_image(cls, request, details):
        request_parameters = details.request_parameters
        prepare_curl_callback, client = cls.get_http_client(details.config)

        user_agent, headers = cls.get_request_headers(request, details)

        url = cls._normalize_url(request_parameters.image_url)
        response = yield cls.fetch(
            client, url, user_agent, headers, details.config, prepare_curl_callback
        )

        if response.code > 399:
            details.status_code = 502
            details.finish_early = True
            details.headers["Thumbor-Http-Loader-Result"] = "Image Not Found"
            details.headers["Thumbor-Http-Loader-Source-StatusCode"] = response.code
            details.body = "Could not load source image: %d (%s)" % (
                response.code,
                response.body,
            )

            return

        details.source_image = response.buffer.read()

    @classmethod
    @tornado.gen.coroutine
    def fetch(cls, client, url, user_agent, headers, config, prepare_curl_callback):
        image_request = tornado.httpclient.HTTPRequest(
            url=url,
            headers=headers,
            connect_timeout=config.HTTP_LOADER_CONNECT_TIMEOUT,
            request_timeout=config.HTTP_LOADER_REQUEST_TIMEOUT,
            follow_redirects=config.HTTP_LOADER_FOLLOW_REDIRECTS,
            max_redirects=config.HTTP_LOADER_MAX_REDIRECTS,
            user_agent=user_agent,
            proxy_host=cls._encode(config.HTTP_LOADER_PROXY_HOST),
            proxy_port=config.HTTP_LOADER_PROXY_PORT,
            proxy_username=cls._encode(config.HTTP_LOADER_PROXY_USERNAME),
            proxy_password=cls._encode(config.HTTP_LOADER_PROXY_PASSWORD),
            ca_certs=cls._encode(config.HTTP_LOADER_CA_CERTS),
            client_key=cls._encode(config.HTTP_LOADER_CLIENT_KEY),
            client_cert=cls._encode(config.HTTP_LOADER_CLIENT_CERT),
            validate_cert=config.HTTP_LOADER_VALIDATE_CERTS,
            prepare_curl_callback=prepare_curl_callback,
        )

        response = yield client.fetch(image_request, raise_error=False)

        return response

    @classmethod
    def _configure_client(cls, impl, max_clients):
        tornado.httpclient.AsyncHTTPClient.configure(impl, max_clients=max_clients)

    @classmethod
    def get_http_client(cls, config, tornado_client=tornado.httpclient.AsyncHTTPClient):
        http_client_implementation = None  # default
        prepare_curl_callback = None

        using_proxy = config.HTTP_LOADER_PROXY_HOST and config.HTTP_LOADER_PROXY_PORT

        # Either using proxy or explicitely, we require curl

        if using_proxy or config.HTTP_LOADER_CURL_ASYNC_HTTP_CLIENT:
            http_client_implementation = "tornado.curl_httpclient.CurlAsyncHTTPClient"
            prepare_curl_callback = cls._get_prepare_curl_callback(config)

        # then we configure tornado to use it
        cls._configure_client(
            http_client_implementation, config.HTTP_LOADER_MAX_CLIENTS
        )

        return prepare_curl_callback, tornado_client()

    @classmethod
    def get_request_headers(cls, request, details):
        user_agent = None
        headers = {}

        if details.config.HTTP_LOADER_FORWARD_ALL_HEADERS:
            headers.update(request.headers)
        else:
            if details.config.HTTP_LOADER_FORWARD_USER_AGENT:
                if "User-Agent" in request.headers:
                    user_agent = request.headers["User-Agent"]

            if details.config.HTTP_LOADER_FORWARD_HEADERS_WHITELIST:
                for header_key in details.config.HTTP_LOADER_FORWARD_HEADERS_WHITELIST:
                    if header_key in request.headers:
                        headers[header_key] = request.headers[header_key]

        if user_agent is None and "User-Agent" not in headers:
            user_agent = details.config.HTTP_LOADER_DEFAULT_USER_AGENT

        return user_agent, headers

    @classmethod
    def _get_prepare_curl_callback(cls, config):
        low_speed_time = config.HTTP_LOADER_CURL_LOW_SPEED_TIME
        low_speed_limit = config.HTTP_LOADER_CURL_LOW_SPEED_LIMIT

        if low_speed_time == 0 or low_speed_limit == 0:
            return None

        class CurlOpts:
            def __init__(self, config):
                self.config = config

            def prepare_curl_callback(self, curl):
                curl.setopt(
                    curl.LOW_SPEED_TIME, self.config.HTTP_LOADER_CURL_LOW_SPEED_TIME
                )
                curl.setopt(
                    curl.LOW_SPEED_LIMIT, self.config.HTTP_LOADER_CURL_LOW_SPEED_LIMIT
                )

        return CurlOpts(config).prepare_curl_callback

    @classmethod
    def _normalize_url(cls, url):
        url = cls._quote_url(url)

        return url if url.startswith("http") else "http://%s" % url

    @classmethod
    def _quote_url(cls, url):
        return cls._encode_url(unquote(url))

    @classmethod
    def _encode_url(cls, url):
        if url == unquote(url):
            return quote(url.encode("utf-8"), safe="~@#$&()*!+=:;,.?/'")

        return url

    @classmethod
    def _encode(cls, string):
        return None if string is None else string.encode("ascii")
