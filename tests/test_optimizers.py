#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com
import os

from os.path import abspath, dirname, join
import tempfile
import unittest
from derpconf.config import Config
from thumbor.context import Context

__dirname = abspath(dirname(__file__))

from thumbor.optimizers.pngcrush import Optimizer as PngcrushOptimizer

fixtures_folder = join(abspath(dirname(__file__)), 'fixtures')


class PngcrushOptimizerTest(unittest.TestCase):
    def setUp(self):
        self.pngcrush_path = '/usr/local/bin/pngcrush'
        if not (os.path.isfile(self.pngcrush_path) and os.access(self.pngcrush_path, os.X_OK)):
            raise unittest.SkipTest("Unable to locate pngcrush at {}".format(self.pngcrush_path))

    def get_context(self):
        conf = Config()
        conf.PNGCRUSH_PATH = self.pngcrush_path
        conf.STATSD_HOST = ''

        return Context(config=conf)

    def test_pngcrush_should_not_run_for_jpeg(self):
        optimizer = PngcrushOptimizer(self.get_context())
        self.assertFalse(optimizer.should_run('jpeg', None))

    def test_pngcrush_should_not_run_for_png(self):
        optimizer = PngcrushOptimizer(self.get_context())
        self.assertTrue(optimizer.should_run('png', None))

    def test_pngcrush_should_optimize_png(self):
        optimizer = PngcrushOptimizer(self.get_context())
        temp = tempfile.NamedTemporaryFile()
        optimizer.optimize(None, fixtures_folder + '/img/fixture2.png', temp.name)

        self.assertLessEqual(os.path.getsize(temp.name), os.path.getsize(fixtures_folder + '/img/fixture2.png'),
                             "pngcrush could not lower filesize for img/fixture1.png")

