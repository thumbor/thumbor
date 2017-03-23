#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2017 tubitv.com yingyu@tubitv.com

from __future__ import unicode_literals, absolute_import
from os.path import abspath, join, dirname

from preggy import expect

from thumbor.context import ServerParameters, RequestParameters
from thumbor.config import Config
from thumbor.engines.mp4 import Engine
from thumbor.utils import which
from thumbor.importer import Importer

from tests.base import TestCase


STORAGE_PATH = abspath(join(dirname(__file__), '../fixtures/images/'))


class Mp4EngineTestCase(TestCase):
    def get_config(self):
        return Config(
            SECURITY_KEY='ACME-SEC',
            ENGINE='thumbor.engines.mp4',
            LOADER="thumbor.loaders.file_loader",
            FILE_LOADER_ROOT_PATH=STORAGE_PATH,
            STORAGE='thumbor.storages.no_storage',
            FFMPEG_PATH=which('ffmpeg'),
            FFPROBE_PATH=which('ffprobe'),
            CONVERT_PATH=which('convert')
        )

    def get_importer(self):
        return Importer(self.config)

    def get_server(self):
        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        return server

    def get_context(self, *args, **kwargs):
        context = super(Mp4EngineTestCase, self).get_context(*args, **kwargs)
        req = RequestParameters(url='/foo/bar.mp4')
        context.request = req
        return context

    def test_create_engine(self):
        engine = Engine(self.context)
        expect(engine).to_be_instance_of(Engine)

    def test_load_video(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, 'test.mp4'), 'r') as im:
            buffer = im.read()
        engine.load(buffer, '.mp4')

    def test_should_return_original(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, 'test.mp4'), 'r') as im:
            buffer = im.read()
        engine.load(buffer, '.mp4')
        result = engine.read('.mp4')
        expect(result).to_equal(engine.buffer)

    def test_encode_to_webp(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, 'test.mp4'), 'r') as im:
            buffer = im.read()
        engine.load(buffer, '.mp4')
        result = engine.read('.webp', 80)
        expect(result[8:12]).to_equal('WEBP')

    def test_encode_to_gif(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, 'test.mp4'), 'r') as im:
            buffer = im.read()
        engine.load(buffer, '.mp4')
        result = engine.read('.gif', 80)
        expect(result[:4]).to_equal('GIF8')
