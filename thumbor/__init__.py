#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com
'''This is the main module in thumbor'''

__version__ = "6.4.1"
__release_date__ = "23-Jan-2018"

# Syntactic sugar imports
try:
    from thumbor.lifecycle.events import Events  # NOQA
    from thumbor.blueprints.engines.engine import Engine  # NOQA
except ImportError:
    print('Failed to import Thumbor\'s lifecycle helpers. Probably setuptools installing thumbor.')
