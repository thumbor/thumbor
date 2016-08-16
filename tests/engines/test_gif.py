#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from __future__ import unicode_literals, absolute_import
from os.path import abspath, join, dirname

from preggy import expect

from thumbor.context import ServerParameters, RequestParameters
from thumbor.config import Config
from thumbor.engines.gif import Engine, GifSicleError
from thumbor.utils import which
from thumbor.importer import Importer

from tests.base import TestCase


STORAGE_PATH = abspath(join(dirname(__file__), '../fixtures/images/'))


class GitEngineTestCase(TestCase):
    def get_config(self):
        return Config(
            SECURITY_KEY='ACME-SEC',
            ENGINE='thumbor.engines.gif',
            IMAGE_METADATA_READ_FORMATS='exif,xmp',
            LOADER="thumbor.loaders.file_loader",
            FILE_LOADER_ROOT_PATH=STORAGE_PATH,
            STORAGE='thumbor.storages.no_storage',
            USE_GIFSICLE_ENGINE=True,
        )

    def get_importer(self):
        return Importer(self.config)

    def get_server(self):
        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        server.gifsicle_path = which('gifsicle')
        return server

    def get_context(self, *args, **kwargs):
        context = super(GitEngineTestCase, self).get_context(*args, **kwargs)
        req = RequestParameters(url='/foo/bar.gif')
        context.request = req
        return context

    def test_create_engine(self):
        engine = Engine(self.context)
        expect(engine).to_be_instance_of(Engine)

    def test_load_image(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, 'animated.gif'), 'r') as im:
            buffer = im.read()
        image = engine.create_image(buffer)
        expect(image.format).to_equal('GIF')

    def test_errors_on_gifsicle_should_raises_errors(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, 'animated.gif'), 'r') as im:
            buffer = im.read()

        engine.load(buffer, '.gif')
        with expect.error_to_happen(
            GifSicleError,
            message='gifsicle command returned errorlevel 1 for command'
                    ' "/usr/local/bin/gifsicle --some-invalid-opt /foo/'
                    'bar.gif" (image maybe corrupted?)'
        ):
            engine.run_gifsicle('--some-invalid-opt')

    def test_is_multiple_should_returns_true_if_gif_has_many_frames(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, 'animated.gif'), 'r') as im:
            buffer = im.read()

        engine.load(buffer, '.gif')
        expect(engine.is_multiple()).to_be_true()

    def test_is_multiple_should_returns_false_if_gif_has_many_frames(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, 'animated-one-frame.gif'), 'r') as im:
            buffer = im.read()

        engine.load(buffer, '.gif')
        expect(engine.is_multiple()).to_be_false()
