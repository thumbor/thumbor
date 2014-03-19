#!/usr/bin/env python
# -*- coding: utf-8 -*-

from shutil import rmtree
from os.path import exists

from tornado.testing import AsyncHTTPTestCase
from tornado.ioloop import IOLoop

from thumbor.app import ThumborServiceApp
from thumbor.importer import Importer
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from integration_tests.urls_helpers import single_dataset  # , combined_dataset


CONFS = {
    'with_pil': {
        'ENGINE': 'thumbor.engines.pil'
    },
}


class PreferencesHandlerTest(AsyncHTTPTestCase):

    def get_app(self):
        storage_path = '/tmp/thumbor-engines-test/'
        if exists(storage_path):
            rmtree(storage_path)

        self.timeout_handle = None
        cfg = Config(SECURITY_KEY='ACME-SEC', FILE_STORAGE_ROOT_PATH=storage_path)
        server_params = ServerParameters(None, None, None, None, None, None)

        cfg.DETECTORS = [
            'thumbor.detectors.face_detector',
            'thumbor.detectors.profile_detector',
            'thumbor.detectors.glasses_detector',
            'thumbor.detectors.feature_detector',
        ]

        conf_key = self._testMethodName.split('__')[1]
        conf = CONFS.get(conf_key, None)
        if conf:
            for key, value in conf.items():
                setattr(cfg, key, value)

        importer = Importer(cfg)
        importer.import_modules()
        ctx = Context(server_params, cfg, importer)
        application = ThumborServiceApp(ctx)

        return application

    def get_new_ioloop(self):
        return IOLoop.instance()

    def retrieve(self, url):
        self.http_client.fetch(self.get_url(url), self.stop)
        return self.wait(timeout=30)

    def test_single_params__with_pil(self):
        single_dataset(self.retrieve)

    # def test_combined_params__with_pil(self):
    #     combined_dataset(self.retrieve)
