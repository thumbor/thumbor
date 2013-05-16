#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import os
from os.path import exists


class BaseStorage(object):
    def __init__(self, context):
        self.context = context

    def put(self, bytes):
        raise NotImplementedError()

    def get(self):
        raise NotImplementedError()

    def ensure_dir(self, path):
        if not exists(path):
            try:
                os.makedirs(path)
            except OSError, err:
                # FILE ALREADY EXISTS = 17
                if err.errno != 17:
                    raise
