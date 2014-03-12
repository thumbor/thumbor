#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
from shutil import rmtree
from os.path import exists
import unittest

from tornado.testing import AsyncHTTPTestCase
from tornado.ioloop import IOLoop
from tornado.stack_context import NullContext

from thumbor.app import ThumborServiceApp
from thumbor.importer import Importer
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from integration_tests.urls_helpers import single_dataset  # , combined_dataset


CONFS = {
    'with_pil': {
        'ENGINE': 'thumbor.engines.pil'
    },
    'with_opencv': {
        'ENGINE': 'thumbor.engines.opencv'
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

    # Overwritten from tornado's AsyncTestCase to fix timeout bug in tornado <2.3
    def wait(self, condition=None, timeout=5):
        if not self._AsyncTestCase__stopped:
            if timeout:
                def timeout_func():
                    try:
                        raise self.failureException(
                            'Async operation timed out after %d seconds' %
                            timeout)
                    except Exception:
                        self._AsyncTestCase__failure = sys.exc_info()
                    self.stop()
                self.timeout_handle = self.io_loop.add_timeout(time.time() + timeout, timeout_func)
            while True:
                self._AsyncTestCase__running = True
                with NullContext():
                    # Wipe out the StackContext that was established in
                    # self.run() so that all callbacks executed inside the
                    # IOLoop will re-run it.
                    self.io_loop.start()
                if (self._AsyncTestCase__failure is not None or
                        condition is None or condition()):
                    break
        if self.timeout_handle:
            self.io_loop.remove_timeout(self.timeout_handle)
            self.timeout_handle = None
        assert self._AsyncTestCase__stopped
        self._AsyncTestCase__stopped = False
        if self._AsyncTestCase__failure is not None:
            # 2to3 isn't smart enough to convert three-argument raise
            # statements correctly in some cases.
            if isinstance(self._AsyncTestCase__failure[1], self._AsyncTestCase__failure[0]):
                raise self._AsyncTestCase__failure[1], None, self._AsyncTestCase__failure[2]
            else:
                raise self._AsyncTestCase__failure[0], self._AsyncTestCase__failure[1], self._AsyncTestCase__failure[2]
        result = self._AsyncTestCase__stop_args
        self._AsyncTestCase__stop_args = None
        return result

    def get_new_ioloop(self):
        return IOLoop.instance()

    def retrieve(self, url):
        self.http_client.fetch(self.get_url(url), self.stop)
        return self.wait(timeout=30)

    def test_single_params__with_pil(self):
        single_dataset(self.retrieve)

    @unittest.expectedFailure
    def test_single_params__with_opencv(self):
        single_dataset(self.retrieve, with_gif=False)

    # def test_combined_params__with_pil(self):
    #     combined_dataset(self.retrieve)

    # def test_combined_params__with_opencv(self):
    #     combined_dataset(self.retrieve, with_gif=False)
