#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import abspath, join, dirname

from pyvows import Vows, expect
from tornado_pyvows.context import TornadoHTTPContext

from thumbor.app import ThumborServiceApp
from thumbor.context import Context, ServerParameters
from thumbor.config import Config
from thumbor.importer import Importer

storage_path = abspath(join(dirname(__file__), 'fixtures/'))


@Vows.batch
class MaxBytesFilterVows(TornadoHTTPContext):

    def get_app(self):
        cfg = Config(SECURITY_KEY='ACME-SEC')
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = storage_path

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        ctx = Context(server, cfg, importer)
        application = ThumborServiceApp(ctx)

        return application

    class WithRegularImage(TornadoHTTPContext):
        def topic(self):
            response = self.get('/unsafe/filters:max_bytes(10000)/conselheira_tutelar.jpg')
            return (response.code, response.body)

        def should_be_200(self, response):
            code, image = response
            expect(code).to_equal(200)
            expect(len(image)).to_be_lesser_or_equal_to(10000)
