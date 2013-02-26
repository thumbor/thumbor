#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com


class BaseStorage(object):
    def __init__(self, context):
        self.context = context

    def put(self, bytes):
        raise NotImplementedError

    def get(self):
        raise NotImplementedError
