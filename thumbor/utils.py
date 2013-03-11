#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import logging
from functools import reduce


def real_import(name):
    if '.' in name:
        return reduce(getattr, name.split('.')[1:], __import__(name))
    return __import__(name)

logger = logging.getLogger('thumbor')
