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

def compile_filters(filter_classes):
    for cls in filter_classes:
        cls.regex = re.compile(cls.regex)

def create_instances(context, filter_classes, filter_params):
    filter_params = filter_params.split(':')
    filter_objs = []
    for param in filter_params:
        filter_instance = firstValid(lambda f: f.init_if_valid(param), filter_classes)
        if filter_instance:
            filter_instance.context = context
            filter_objs.append(filter_instance)
    return filter_objs

class BaseFilter(object):

    def __init__(self, params):
        self.params = self.regex.match(params)
        if self.params:
            self.params = self.params.groupdict()

    def is_valid(self):
        return bool(self.params)

    @classmethod
    def init_if_valid(cls, param):
        instance = cls(param)
        if instance.is_valid():
            return instance
        else:
            return None
