#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect
from tornado_pyvows.context import TornadoHTTPContext

from thumbor.app import ThumborServiceApp
from thumbor.importer import Importer
from thumbor.config import Config
from thumbor.context import Context, ServerParameters

from os.path import abspath, join, dirname, exists
from shutil import rmtree


class BaseContext(TornadoHTTPContext):
    def get_app(self):
        file_storage_root_path = '/tmp/thumbor-vows/storage'
        if exists(file_storage_root_path):
            rmtree(file_storage_root_path)

        cfg = Config()
        cfg.USE_BLACKLIST = True
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = abspath(join(dirname(__file__), 'fixtures/'))
        cfg.STORAGE = 'thumbor.storages.file_storage'
        cfg.FILE_STORAGE_ROOT_PATH = file_storage_root_path

        importer = Importer(cfg)
        importer.import_modules()

        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'debug', None)
        ctx = Context(server, cfg, importer)
        application = ThumborServiceApp(ctx)
        return application


@Vows.batch
class BlacklistIntegration(BaseContext):

    class NormalGetImage(TornadoHTTPContext):
        def topic(self):
            response = self.get('/unsafe/image.jpg')
            return response.code

        def should_return_200(self, topic):
            expect(topic).to_equal(200)

        class BlacklistedGetImage(TornadoHTTPContext):

            def topic(self):
                self.fetch('/blacklist?image.jpg', method='PUT', body='')
                response = self.get('/unsafe/image.jpg')
                return response.code

            def should_return_bad_request(self, topic):
                expect(topic).to_equal(400)
