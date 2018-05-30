#!/usr/bin/python
# -*- coding: utf-8 -*-
'''Base infrastructure of integration tests for thumbor'''

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from os.path import join, exists
import random
import tempfile
from uuid import uuid4

import tornado.gen as gen
from tornado.testing import AsyncHTTPTestCase
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from preggy import assertion
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
        raise RuntimeError("Can't calculate SSIM for images of different "
                           "sizes (one is %dx%d, the other %dx%d)." % (
                               actual.size[0],
                               actual.size[1],
                               expected.size[0],
                               expected.size[1],
                           ))

    return compute_ssim(actual, expected)


@assertion
def to_be_similar_to(topic, expected):
    '''Ensure images are similar.'''
    if topic is None or not isinstance(topic, bytes):
        raise AssertionError(
            f'Topic must not to be of type bytes and not empty.')

    if expected is None or not isinstance(expected, (Image.Image,)):
        raise AssertionError(f'Expected image ({expected}) must not be None '
                             'and must be of type PIL.Image.')

    topic_image = Image.open(BytesIO(topic))

    sim_analysis = get_ssim(topic_image, expected)
    if sim_analysis < 0.95:
        store_dir = tempfile.gettempdir()
        test_id = uuid4()
        topic_path = join(store_dir,
                          f'{test_id}-topic.{topic_image.format.lower()}')
        expected_path = join(store_dir,
                             f'{test_id}-expected.{expected.format.lower()}')

        topic_image.save(topic_path)
        expected.save(expected_path)

        raise AssertionError(
            f'Topic image should be at least 95% similar to '
            f'expected image, but the similarity was of {sim_analysis*100}%. '
            f'The images can be found at:\n{topic_path}\n{expected_path}')


@assertion
def not_to_be_similar_to(topic, expected):
    try:
        to_be_similar_to(topic, expected)
        raise AssertionError(
            'Expected topic image to be less than 95% similar '
            'to expected image, but it wasn\'t.',)
    except AssertionError:
        return True


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

    def get_fixture_path(self, name):
        'Returns a fixture path'
        return f'{self.fixture_path}/{name}'

    def get_fixture(self, name):
        'Gets a fixture image'
        fpath = self.get_fixture_path(name)
        assert exists(fpath)
        image = Image.open(fpath)
        conv_image = image.convert('RGB')
        conv_image.format = image.format
        return conv_image

    def debug_image(self, image):
        'Stores the image buffer in a temp file'
        image = Image.fromarray(image)
        path = '/tmp/debug_image_%s.jpg' % random.randint(1, 10000)
        image.save(path, 'JPEG')
        print('The debug image was in %s.' % path)

    def debug_size(self, image):
        'Prints the image dimensions'
        image = Image.fromarray(image)
        print("Image dimensions are %dx%d (shape is %s)" %
              (image.size[0], image.size[1], image.shape))

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
