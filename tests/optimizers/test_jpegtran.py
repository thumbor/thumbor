#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import abspath, join, dirname

from thumbor.config import Config
from thumbor.context import Context
from thumbor.optimizers.jpegtran import Optimizer
from unittest import TestCase


class JpegtranOptimizerTest(TestCase):
    def get_optimizer(self):
        conf = Config()
        conf.STATSD_HOST = ''
        ctx = Context(config=conf)
        optimizer = Optimizer(ctx)

        return optimizer

    def test_should_run_for_jpeg(self):
        optimizer = self.get_optimizer()
        self.assertTrue(optimizer.should_run('.jpg', ''))
        self.assertTrue(optimizer.should_run('.jpeg', ''))

    def test_should_not_run_for_not_jpeg(self):
        optimizer = self.get_optimizer()

        self.assertFalse(optimizer.should_run('.png', ''))
        self.assertFalse(optimizer.should_run('.webp', ''))
        self.assertFalse(optimizer.should_run('.gif', ''))

    def test_should_optimize(self):
        optimizer = self.get_optimizer()
        fixtures = abspath(join(dirname(__file__), '../fixtures/images/'))
        with open(fixtures + '/Christophe_Henner_-_June_2016.jpg', 'rb') as f:
            input_bufer = f.read()
        return_buffer = optimizer.run_optimizer('.jpg', input_bufer)

        self.assertLessEqual(len(return_buffer), len(input_bufer),
                             "jpegtran could not lower filesize for images/image.jpg")

    def test_should_return_old_buffer_for_invalid_extension(self):
        optimizer = self.get_optimizer()
        buffer = 'garbage'
        return_buffer = optimizer.run_optimizer('.png', buffer)

        self.assertEqual(return_buffer, buffer)

    def test_should_return_old_buffer_for_invalid_image(self):
        optimizer = self.get_optimizer()
        buffer = 'garbage'
        return_buffer = optimizer.run_optimizer('.jpg', buffer)

        self.assertEqual(return_buffer, buffer)
