#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com
from os.path import abspath, join, dirname

from pyvows import Vows, expect
from tornado_pyvows.context import TornadoHTTPContext

from thumbor.app import ThumborServiceApp
from thumbor.importer import Importer
from thumbor.config import Config
from thumbor.context import Context, ServerParameters


fixture_for = lambda path: abspath(join(dirname(__file__), 'fixtures', path))


def get_url():
    return '/unsafe/smart/alabama1_ap620.jpg'


def get_app(prevent_result_storage=False, detection_error=False):
    cfg = Config.load(fixture_for('max_age_conf.py'))
    server_params = ServerParameters(None, None, None, None, None, None)

    cfg.DETECTORS = []
    if prevent_result_storage:
        cfg.DETECTORS.append('fixtures.prevent_result_storage_detector')
    if detection_error:
        cfg.DETECTORS.append('fixtures.detection_error_detector')

    importer = Importer(cfg)
    importer.import_modules()
    ctx = Context(server_params, cfg, importer)
    application = ThumborServiceApp(ctx)

    return application


# commented til we fix tornado-pyvows issue
#@Vows.batch
class MaxAgeVows(Vows.Context):

    class WithRegularImage(TornadoHTTPContext):
        def get_app(self):
            return get_app()

        def topic(self):
            response = self.get(get_url())
            return (response.code, response.headers)

        def should_be_200(self, response):
            code, _ = response
            expect(code).to_equal(200)

        def should_set_cache_control(self, response):
            _, headers = response
            expect(headers['Cache-Control']).to_equal('max-age=2,public')

        def should_set_expires(self, response):
            _, headers = response
            expect(headers).to_include('Expires')


    class WithNonStoragedImage(TornadoHTTPContext):
        def get_app(self):
            return get_app(prevent_result_storage=True)

        def topic(self):
            response = self.get(get_url())
            return (response.code, response.headers)

        def should_be_200(self, response):
            code, _ = response
            expect(code).to_equal(200)

        def should_set_cache_control(self, response):
            _, headers = response
            expect(headers['Cache-Control']).to_equal('max-age=1,public')

        def should_set_expires(self, response):
            _, headers = response
            expect(headers).to_include('Expires')


    class WithDetectionErrorImage(TornadoHTTPContext):
        def get_app(self):
            return get_app(detection_error=True)

        def topic(self):
            response = self.get(get_url())
            return (response.code, response.headers)

        def should_be_200(self, response):
            code, _ = response
            expect(code).to_equal(200)

        def should_set_cache_control(self, response):
            _, headers = response
            expect(headers['Cache-Control']).to_equal('max-age=1,public')

        def should_set_expires(self, response):
            _, headers = response
            expect(headers).to_include('Expires')
