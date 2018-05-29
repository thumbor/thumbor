#!/usr/bin/python
# -*- coding: utf-8 -*-
'''Base infrastructure of integration tests for thumbor'''

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from os.path import join, dirname, realpath, exists

import tornado.gen as gen
from tornado.testing import AsyncHTTPTestCase
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from preggy import create_assertions
from ssim import compute_ssim
from PIL import Image
from six import BytesIO

from thumbor.server import load_importer, bind_blueprints
from thumbor.app import ThumborServiceApp
from thumbor.context import Context
from thumbor.config import Config


def get_ssim(actual, expected):
    'Returns the ssim between two images'
    if actual.size[0] != expected.size[0] or actual.size[1] != expected.size[1]:
        raise RuntimeError(
            "Can't calculate SSIM for images of different sizes (one is %dx%d, the other %dx%d)."
            % (
                actual.size[0],
                actual.size[1],
                expected.size[0],
                expected.size[1],
            ))

    return compute_ssim(actual, expected)


@create_assertions
def to_be_similar_to(topic, expected):
    '''Ensure images are similar.'''
    topic_image = Image.open(BytesIO(topic))

    fixture_path = join(
        dirname(realpath(__file__)), '..', 'fixtures', 'filters')

    expected_path = realpath(f'{fixture_path}/{expected}')
    if not exists(expected_path):
        return False

    with open(expected_path, 'rb') as image:
        expected_image = Image.open(BytesIO(image.read()))

    return get_ssim(topic_image, expected_image) > 0.95


class TestCase(AsyncHTTPTestCase):
    '''Base class for all thumbor's integration test cases'''

    def __init__(self, *a, **kw):
        super(TestCase, self).__init__(*a, **kw)
        self.config = None
        self.server = None
        self.importer = None
        self.request_handler = None

    def get_app(self):
        self.context = self.get_context()
        app = ThumborServiceApp(self.context)
        bind_blueprints(self.context.modules.importer)
        return app

    def get_config(self):  # pylint: disable=no-self-use
        'Gets default config. Can be overriden.'
        return Config()

    def get_server(self):  # pylint: disable=no-self-use
        'Gets default server. Can be overriden.'
        return None

    def get_importer(self):
        'Gets default importer. Can be overriden.'
        return load_importer(self.get_config())

    def get_request_handler(self):  # pylint: disable=no-self-use
        'Gets default request handler. Can be overriden.'
        return None

    def get_context(self):
        'Gets the default context.'
        self.config = self.get_config()
        self.server = self.get_server()
        self.importer = self.get_importer()
        self.request_handler = self.get_request_handler()
        return Context(self.server, self.config, self.importer,
                       self.request_handler)

    @gen.coroutine
    def get(self, path, headers=None):
        'Get a resource in thumbor with the specified path'
        if headers is None:
            headers = {}

        client = AsyncHTTPClient()

        req = HTTPRequest(
            url=self.get_url(path),
            headers=headers,
            method='GET',
        )
        response = yield client.fetch(req)
        return response

    # def get(self, path, headers={}):
    # 'Get a resource in thumbor with the specified path'
    # return self.fetch(
    # path,
    # method='GET',
    # body=urlencode({}, doseq=True),
    # headers=headers,
    # allow_nonstandard_methods=True)

    # def post(self, path, headers, body):
    # return self.fetch(
    # path,
    # method='POST',
    # body=body,
    # headers=headers,
    # allow_nonstandard_methods=True)

    # def put(self, path, headers, body):
    # return self.fetch(
    # path,
    # method='PUT',
    # body=body,
    # headers=headers,
    # allow_nonstandard_methods=True)

    # def delete(self, path, headers):
    # return self.fetch(
    # path,
    # method='DELETE',
    # body=urlencode({}, doseq=True),
    # headers=headers,
    # allow_nonstandard_methods=True)
