#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from unittest import TestCase

import thumbor_plugins.optimizers.gifv

import thumbor.optimizers.gifv


class GifvOptimizerTest(TestCase):
    def test_should_be_subclass_of_thumbor_plugins(self):
        self.assertTrue(
            issubclass(
                thumbor.optimizers.gifv.Optimizer,
                thumbor_plugins.optimizers.gifv.Optimizer,
            )
        )
