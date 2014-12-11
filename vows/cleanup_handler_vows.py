#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import os
from os.path import abspath, join, dirname, exists
from shutil import rmtree
from urllib import quote

from pyvows import Vows, expect
from tornado_pyvows.context import TornadoHTTPContext

from thumbor.app import ThumborServiceApp
from thumbor.importer import Importer
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.engines.pil import Engine as PILEngine
from thumbor.storages.file_storage import Storage as FileStorage

storage_path = abspath(join(dirname(__file__), 'fixtures/'))

FILE_STORAGE_ROOT_PATH = '/tmp/thumbor-vows/cleanup_handler_vows'
RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = '/tmp/thumbor-vows/cleanup_handler_result_vows'

stored_original_file = "%s/%s" % (FILE_STORAGE_ROOT_PATH, "42/573d7391a7bc9dcdef39375562aa088c386c85")
stored_original_file2 = "%s/%s" % (FILE_STORAGE_ROOT_PATH, "9f/ab80cf3ee85222531cdf226c17519b5f64c4a6")
stored_result_file = "%s/%s" % (RESULT_STORAGE_FILE_STORAGE_ROOT_PATH, "/v2/_w/IU/_wIUeSaeHw8dricKG2MGhqu5thk=/smart/image.jpg")
stored_result_file2 = "%s/%s" % (RESULT_STORAGE_FILE_STORAGE_ROOT_PATH, "/v2/YF/5M/YF5MwqgThS_B9IpDH9DXpLLYizo=/smart/hidrocarbonetos_9.jpg")

class BaseContext(TornadoHTTPContext):
    def __init__(self, *args, **kw):
        super(BaseContext, self).__init__(*args, **kw)

@Vows.batch
class CleanupHandlerCheck(TornadoHTTPContext):
    def get_app(self):
        cfg = Config(SECURITY_KEY='ACME-SEC')
        cfg.CUSTOM_HANDLERS = ['thumbor.handlers.cleanup']
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = storage_path
        cfg.STORAGE = "thumbor.storages.file_storage"
        cfg.FILE_STORAGE_ROOT_PATH = FILE_STORAGE_ROOT_PATH
        if exists(FILE_STORAGE_ROOT_PATH):
            rmtree(FILE_STORAGE_ROOT_PATH)

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        ctx = Context(server, cfg, importer)
        application = ThumborServiceApp(ctx)

        return application

    class without_unsafe_url_image(TornadoHTTPContext):
        def topic(self):
            response = self.delete('/original/JrDF8vTWrBFiiOsVMmcCtP3PFCk=/alabama1_ap620%C3%A9.jpg')
            return (response.code, response.headers)

        def should_be_404(self, response):
            code, _ = response
            expect(code).to_equal(404)

    class without_image(TornadoHTTPContext):
        def topic(self):
            response = self.delete('/original/JrDF8vTWrBFiiOsVMmcCtP3PFCk=/unsafe/')
            return (response.code, response.headers)

        def should_be_404(self, response):
            code, _ = response
            expect(code).to_equal(404)

    class with_unsafe_url_image(TornadoHTTPContext):
        def setup(self):
            self.get('/unsafe/alabama1_ap620%C3%A9.jpg')

        def topic(self):
            response = self.delete('/original/JrDF8vTWrBFiiOsVMmcCtP3PFCk=/unsafe/alabama1_ap620%C3%A9.jpg')
            return (response.code, response.headers)

        def should_be_204(self, response):
            code, _ = response
            expect(code).to_equal(204)

    class with_UTF8_URLEncoded_image_name_using_encoded_url(TornadoHTTPContext):
        def setup(self):
            self.get('/lc6e3kkm_2Ww7NWho8HPOe-sqLU=/smart/alabama1_ap620%C3%A9.jpg')

        def topic(self):
            url = '/original/u6d2yBspIvwpmUv-aFph68hPonQ=/lc6e3kkm_2Ww7NWho8HPOe-sqLU=/smart/alabama1_ap620%C3%A9.jpg'
            response = self.delete(url)
            return (response.code, response.headers)

        def should_be_204(self, response):
            code, _ = response
            expect(code).to_equal(204)

    class with_unexistent_image(TornadoHTTPContext):
        def topic(self):
            response = self.delete('/original/JrDF8vTWrBFiiOsVMmcCtP3PFCk=/unsafe/alabama1_ap620%C3%A9.jpg')
            return (response.code, response.headers)

        def should_be_404(self, response):
            code, _ = response
            expect(code).to_equal(404)

@Vows.batch
class DeleteImageWithoutUnsafe(BaseContext):
    def get_app(self):
        cfg = Config(SECURITY_KEY='ACME-SEC')
        cfg.CUSTOM_HANDLERS = ['thumbor.handlers.cleanup']
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = storage_path
        cfg.STORAGE = "thumbor.storages.file_storage"
        cfg.ALLOW_UNSAFE_URL = False
        cfg.FILE_STORAGE_ROOT_PATH = FILE_STORAGE_ROOT_PATH
        if exists(FILE_STORAGE_ROOT_PATH):
            rmtree(FILE_STORAGE_ROOT_PATH)

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8890, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        ctx = Context(server, cfg, importer)
        application = ThumborServiceApp(ctx)

        return application

    class WithSignedRegularImage(TornadoHTTPContext):
        def setup(self):
            self.get('/_wIUeSaeHw8dricKG2MGhqu5thk=/smart/image.jpg')

        def topic(self):
            response = self.delete('/original/nA_PG5f_rx3o3Ohlh-JKXazuoBA=/_wIUeSaeHw8dricKG2MGhqu5thk=/smart/image.jpg')
            return (response.code, response.headers)

        def should_be_204(self, response):
            code, _ = response
            expect(code).to_equal(204)

    class WithWrongSignedRegularImage(TornadoHTTPContext):
        def topic(self):
            response = self.delete('/original/An_PG5f_rx3o3Ohlh-JKXazuoBA=/_wIUeSaeHw8dricKG2MGhqu5thk=/smart/image.jpg')
            return (response.code, response.headers)

        def should_be_404(self, response):
            code, _ = response
            expect(code).to_equal(404)

    class WithRegularImage(TornadoHTTPContext):
        def topic(self):
            response = self.delete('/original/AKUpqMnLJ9GeEmdnFGAc_D1urQg=/unsafe/smart/image.jpg')
            return (response.code, response.headers)

        def should_be_404(self, response):
            code, _ = response
            expect(code).to_equal(404)

@Vows.batch
class CheckingImageWasCleaned(BaseContext):
    def get_app(self):
        cfg = Config(SECURITY_KEY='ACME-SEC')
        cfg.CUSTOM_HANDLERS = ['thumbor.handlers.cleanup']
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = storage_path
        cfg.STORAGE = "thumbor.storages.file_storage"
        cfg.FILE_STORAGE_ROOT_PATH = FILE_STORAGE_ROOT_PATH
        if exists(FILE_STORAGE_ROOT_PATH):
            rmtree(FILE_STORAGE_ROOT_PATH)

        cfg.RESULT_STORAGE = "thumbor.result_storages.file_storage"
        cfg.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = RESULT_STORAGE_FILE_STORAGE_ROOT_PATH
        if exists(RESULT_STORAGE_FILE_STORAGE_ROOT_PATH):
            rmtree(RESULT_STORAGE_FILE_STORAGE_ROOT_PATH)

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8891, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        ctx = Context(server, cfg, importer)
        application = ThumborServiceApp(ctx)

        return application

    class DeletingOriginalImage(TornadoHTTPContext):
        def setup(self):
            self.get('/_wIUeSaeHw8dricKG2MGhqu5thk=/smart/image.jpg')

        def topic(self):
            response = self.delete('/original/nA_PG5f_rx3o3Ohlh-JKXazuoBA=/_wIUeSaeHw8dricKG2MGhqu5thk=/smart/image.jpg')
            return (response.code, response.headers)

        def should_be_keep_the_result_image(self, response):
            code, _ = response
            expect(code).to_equal(204)
            expect(exists(stored_original_file)).to_equal(False)
            expect(exists(stored_result_file)).to_equal(True)

    class DeletingResultImage(TornadoHTTPContext):
        def setup(self):
            self.get('/YF5MwqgThS_B9IpDH9DXpLLYizo=/smart/hidrocarbonetos_9.jpg')

        def topic(self):
            response = self.delete('/result/h1jMkQgyzZuVJsvRLIYsts85_4Y=/YF5MwqgThS_B9IpDH9DXpLLYizo=/smart/hidrocarbonetos_9.jpg')
            return (response.code, response.headers)

        def should_be_keep_the_original_image(self, response):
            code, _ = response
            expect(code).to_equal(204)
            expect(exists(stored_original_file2)).to_equal(True)
            expect(exists(stored_result_file2)).to_equal(False)

@Vows.batch
class DeleteResultImageWithoutResultStorage(BaseContext):
    def get_app(self):
        cfg = Config(SECURITY_KEY='ACME-SEC')
        cfg.CUSTOM_HANDLERS = ['thumbor.handlers.cleanup']
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = storage_path
        cfg.STORAGE = "thumbor.storages.file_storage"
        cfg.FILE_STORAGE_ROOT_PATH = FILE_STORAGE_ROOT_PATH
        if exists(FILE_STORAGE_ROOT_PATH):
            rmtree(FILE_STORAGE_ROOT_PATH)

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8890, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        ctx = Context(server, cfg, importer)
        application = ThumborServiceApp(ctx)

        return application

    class WhenRunning(TornadoHTTPContext):
        def topic(self):
            response = self.delete('/result/vJe5HXzQul3XeRENGjuA-qI3j6c=/iUoB6VSZ1gocza4Qu87WvEcVfbw=/smart/image2.jpg')
            return (response.code, response.headers)

        def should_be_404(self, response):
            code, _ = response
            expect(code).to_equal(404)
