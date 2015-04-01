#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import abspath, join, dirname
from json import loads

from pyvows import Vows, expect
from tornado_pyvows.context import TornadoHTTPContext

from thumbor.app import ThumborServiceApp
from thumbor.importer import Importer
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.utils import which

storage_path = abspath(join(dirname(__file__), 'fixtures/'))


class BaseContext(TornadoHTTPContext):
    def __init__(self, *args, **kw):
        super(BaseContext, self).__init__(*args, **kw)


@Vows.batch
class GetMeta(BaseContext):
    def get_app(self):
        cfg = Config(
            SECURITY_KEY='ACME-SEC',
            LOADER='thumbor.loaders.file_loader',
            RESULT_STORAGE='thumbor.result_storages.file_storage',
            RESULT_STORAGE_STORES_UNSAFE=True,
            RESULT_STORAGE_EXPIRATION_SECONDS=2592000,
            FILE_LOADER_ROOT_PATH=storage_path,
            OPTIMIZERS=[
                'thumbor.optimizers.jpegtran'
            ]
        )

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        ctx = Context(server, cfg, importer)
        application = ThumborServiceApp(ctx)

        return application

    class WithMetadata(TornadoHTTPContext):
        def topic(self):
            response = self.get('/unsafe/meta/800x400/image.jpg')
            return (response.code, response.headers)

        def should_be_200(self, response):
            code, _ = response
            expect(code).to_equal(200)

        class FromCacheWithMetadata(TornadoHTTPContext):
            def topic(self):
                response = self.get('/unsafe/meta/800x400/image.jpg')
                return (response.code, response.headers)

            def should_be_200(self, response):
                code, _ = response
                expect(code).to_equal(200)


@Vows.batch
class GetMetaWithoutStorage(BaseContext):
    def get_app(self):
        cfg = Config(
            SECURITY_KEY='ACME-SEC',
            LOADER='thumbor.loaders.file_loader',
            RESULT_STORAGE='thumbor.result_storages.file_storage',
            RESULT_STORAGE_STORES_UNSAFE=False,
            RESULT_STORAGE_EXPIRATION_SECONDS=2592000,
            FILE_LOADER_ROOT_PATH=storage_path,
            STORAGE='thumbor.storages.no_storage',
            OPTIMIZERS=[
                'thumbor.optimizers.jpegtran'
            ]
        )

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        ctx = Context(server, cfg, importer)
        application = ThumborServiceApp(ctx)

        return application

    class WithMetadata(TornadoHTTPContext):
        def topic(self):
            response = self.get('/unsafe/meta/800x400/image.jpg')
            return (response.code, response.headers)

        def should_be_200(self, response):
            code, _ = response
            expect(code).to_equal(200)


@Vows.batch
class GetMetaFrameCount(BaseContext):
    def get_app(self):
        cfg = Config(
            SECURITY_KEY='ACME-SEC',
            LOADER='thumbor.loaders.file_loader',
            RESULT_STORAGE_STORES_UNSAFE=False,
            RESULT_STORAGE_EXPIRATION_SECONDS=2592000,
            FILE_LOADER_ROOT_PATH=storage_path,
            OPTIMIZERS=[],
            USE_GIFSICLE_ENGINE=True,
        )

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        server.gifsicle_path = which('gifsicle')
        ctx = Context(server, cfg, importer)
        application = ThumborServiceApp(ctx)

        return application

    class WithStaticImage(TornadoHTTPContext):
        def topic(self):
            response = self.get('/unsafe/meta/image.jpg')
            return (response.code, response.headers, response.body)

        def should_be_200(self, response):
            code, headers, body = response
            expect(code).to_equal(200)

        def should_have_frame_count(self, response):
            expect(response[0]).to_equal(200)
            obj = loads(response[2])

            expect(obj['thumbor']['source']['frameCount']).to_equal(1)

    class WithAnimatedImage(TornadoHTTPContext):
        def topic(self):
            response = self.get('/unsafe/meta/animated_image.gif')
            return (response.code, response.headers, response.body)

        def should_be_200(self, response):
            code, headers, body = response
            expect(code).to_equal(200)

        def should_have_frame_count(self, response):
            expect(response[0]).to_equal(200)
            obj = loads(response[2])

            expect(obj['thumbor']['source']['frameCount']).to_equal(2)
