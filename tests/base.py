#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import random
import unicodedata
from io import BytesIO
from unittest import TestCase as PythonTestCase
import urllib
import mimetypes
from os.path import exists, realpath, dirname, join
import cStringIO
import mock

import numpy as np
from PIL import Image
from ssim import compute_ssim
from preggy import create_assertions

from thumbor.app import ThumborServiceApp
from thumbor.context import Context, RequestParameters
from thumbor.config import Config
from thumbor.importer import Importer
from thumbor.transformer import Transformer
from thumbor.engines.pil import Engine as PilEngine

from tornado.testing import AsyncHTTPTestCase


@create_assertions
def to_exist(topic):
    return exists(topic)


def normalize_unicode_path(path):
    normalized_path = path
    for format in ['NFD', 'NFC', 'NFKD', 'NFKC']:
        normalized_path = unicodedata.normalize(format, unicode(path))
        if exists(normalized_path):
            break
    return normalized_path


@create_assertions
def to_be_the_same_as(topic, expected):
    topic = normalize_unicode_path(topic)
    expected = normalize_unicode_path(expected)

    if not exists(topic):
        raise AssertionError("File at %s does not exist" % topic)
    if not exists(expected):
        raise AssertionError("File at %s does not exist" % expected)

    im = Image.open(topic)
    im = im.convert('RGBA')
    topic_contents = np.array(im)

    im = Image.open(expected)
    im = im.convert('RGBA')
    expected_contents = np.array(im)

    return get_ssim(topic_contents, expected_contents) > 0.95


@create_assertions
def to_be_similar_to(topic, expected):
    im = Image.open(cStringIO.StringIO(topic))
    im = im.convert('RGBA')
    topic_contents = np.array(im)

    im = Image.open(cStringIO.StringIO(expected))
    im = im.convert('RGBA')
    expected_contents = np.array(im)

    return get_ssim(topic_contents, expected_contents) > 0.95


@create_assertions
def to_be_webp(topic):
    im = Image.open(cStringIO.StringIO(topic))
    return im.format.lower() == 'webp'


@create_assertions
def to_be_png(topic):
    im = Image.open(cStringIO.StringIO(topic))
    return im.format.lower() == 'png'


@create_assertions
def to_be_gif(topic):
    im = Image.open(cStringIO.StringIO(topic))
    return im.format.lower() == 'gif'


@create_assertions
def to_be_jpeg(topic):
    im = Image.open(cStringIO.StringIO(topic))
    return im.format.lower() == 'jpeg'


def get_ssim(actual, expected):
    im = Image.fromarray(actual)
    im2 = Image.fromarray(expected)

    if im.size[0] != im2.size[0] or im.size[1] != im2.size[1]:
        raise RuntimeError(
            "Can't calculate SSIM for images of different sizes (one is %dx%d, the other %dx%d)." % (
                im.size[0], im.size[1],
                im2.size[0], im2.size[1],
            )
        )

    return compute_ssim(im, im2)


@create_assertions
def to_be_resized(image):
    return image.has_resized_properly()


@create_assertions
def to_be_cropped(image):
    return image.has_cropped_properly()


def encode_multipart_formdata(fields, files):
    BOUNDARY = 'thumborUploadFormBoundary'
    CRLF = '\r\n'
    L = []
    for key, value in fields.items():
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % mimetypes.guess_type(filename)[0] or 'application/octet-stream')
        L.append('')
        L.append(value)
    L.append('')
    L.append('')
    L.append('--' + BOUNDARY + '--')
    body = CRLF.join([str(item) for item in L])
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body


class TestCase(AsyncHTTPTestCase):
    _multiprocess_can_split_ = True

    def get_app(self):
        self.context = self.get_context()
        return ThumborServiceApp(self.context)

    def get_context(self):
        return Context(None, Config(), None)

    def get(self, path, headers):
        return self.fetch(path,
                          method='GET',
                          body=urllib.urlencode({}, doseq=True),
                          headers=headers,
                          allow_nonstandard_methods=True)

    def post(self, path, headers, body):
        return self.fetch(path,
                          method='POST',
                          body=body,
                          headers=headers,
                          allow_nonstandard_methods=True)

    def put(self, path, headers, body):
        return self.fetch(path,
                          method='PUT',
                          body=body,
                          headers=headers,
                          allow_nonstandard_methods=True)

    def delete(self, path, headers):
        return self.fetch(path,
                          method='DELETE',
                          body=urllib.urlencode({}, doseq=True),
                          headers=headers,
                          allow_nonstandard_methods=True)

    def post_files(self, path, data={}, files=[]):
        multipart_data = encode_multipart_formdata(data, files)

        return self.fetch(path,
                          method='POST',
                          body=multipart_data[1],
                          headers={
                              'Content-Type': multipart_data[0]
                          },
                          allow_nonstandard_methods=True)


class FilterTestCase(PythonTestCase):
    _multiprocess_can_split_ = True

    def setUp(self):
        self.context = {}

    def get_filter(self, filter_name, params_string="", config_context=None):
        config = Config(
            FILTERS=[filter_name],
            LOADER='thumbor.loaders.file_loader',
            FILE_LOADER_ROOT_PATH=join(dirname(realpath(__file__)), 'fixtures', 'filters')
        )
        importer = Importer(config)
        importer.import_modules()

        req = RequestParameters()

        context = Context(config=config, importer=importer)
        context.request = req
        context.request.engine = context.modules.engine

        if config_context is not None:
            config_context(context)

        self.context = context

        fltr = importer.filters[0]
        fltr.pre_compile()

        context.transformer = Transformer(context)

        return fltr(params_string, context=context)

    def get_fixture_path(self, name):
        return './tests/fixtures/filters/%s' % name

    def get_fixture(self, name):
        im = Image.open(self.get_fixture_path(name))
        im = im.convert('RGBA')
        return np.array(im)

    def get_filtered(self, source_image, filter_name, params_string, config_context=None):
        fltr = self.get_filter(filter_name, params_string, config_context)
        im = Image.open(self.get_fixture_path(source_image))
        img_buffer = BytesIO()
        im.save(img_buffer, 'JPEG', quality=100)

        fltr.engine.load(img_buffer.getvalue(), '.jpg')
        fltr.context.transformer.img_operation_worker()

        fltr.run()

        fltr.engine.image = fltr.engine.image.convert('RGBA')

        return np.array(fltr.engine.image)

    def get_ssim(self, actual, expected):
        return get_ssim(actual, expected)

    def debug(self, image):
        im = Image.fromarray(image)
        path = '/tmp/debug_image_%s.jpg' % random.randint(1, 10000)
        im.save(path, 'JPEG')
        print 'The debug image was in %s.' % path

    def debug_size(self, image):
        im = Image.fromarray(image)
        print "Image dimensions are %dx%d (shape is %s)" % (im.size[0], im.size[1], image.shape)


class DetectorTestCase(PythonTestCase):
    _multiprocess_can_split_ = True

    def setUp(self):
        self.context = mock.Mock(request=mock.Mock(focal_points=[]))
        self.engine = PilEngine(self.context)
        self.context.modules.engine = self.engine
