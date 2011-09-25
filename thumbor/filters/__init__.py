#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import re

def firstValid(f, it):
    for el in it:
        obj = f(el)
        if obj:
            return obj
    return None

class BaseFilter(object):

    def __init__(self, params):
        self.params = re.match(self.regex, params)
        if self.params:
            self.params = self.params.groupdict()

    def is_valid(self):
        return bool(self.params)

    @classmethod
    def initialize(cls, filters, filter_params):
        filter_params = filter_params.split(':')
        filter_objs = map(lambda param: firstValid(lambda f: f.init_if_valid(param), filters), filter_params)
        return filter(lambda f: f, filter_objs)

    @classmethod
    def init_if_valid(cls, param):
        instance = cls(param)
        if instance.is_valid():
            return instance
        else:
            return None
