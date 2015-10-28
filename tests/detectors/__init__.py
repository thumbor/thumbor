#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from unittest import TestCase
import mock

from thumbor.engines.pil import Engine as PilEngine


class DetectorTestCase(TestCase):
    _multiprocess_can_split_ = True

    def setUp(self):
        self.context = mock.Mock(request=mock.Mock(focal_points=[]))
        self.engine = PilEngine(self.context)
        self.context.modules.engine = self.engine
