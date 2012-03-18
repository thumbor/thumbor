#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import re

def create_instances(context, filter_classes, filter_params):
    filter_params = filter_params.split(':')
    filter_objs = []

    for param in filter_params:
        for cls in filter_classes:
            if not cls.compiled: cls.pre_compile()
            instance = cls.init_if_valid(param)
            if instance: break

        if instance:
            instance.context = context
            if context.modules and context.modules.engine:
                instance.engine = context.modules.engine
            filter_objs.append(instance)
    return filter_objs

def filter_method(*args, **kwargs):
    def _filter_deco(fn):
        def wrapper(self, *args2):
            return fn(self, *args2)
        wrapper.filter_data = {
            'name': fn.__name__,
            'params': args,
            'async': kwargs.get('async', False)
        }
        return wrapper
    return _filter_deco


class BaseFilter(object):

    PositiveNumber = {
        'regex': r'[\d]+',
        'parse': int
    }
    NegativeNumber = {
        'regex': r'[-]%s' % PositiveNumber['regex'],
        'parse': int
    }
    Number = {
        'regex': r'[-]?%s' % PositiveNumber['regex'],
        'parse': int
    }
    DecimalNumber = {
        'regex': r'[-]?(?:(?:[\d]+\.?[\d]*)|(?:[\d]*\.?[\d]+))',
        'parse': float
    }
    Boolean = {
        'regex': r'[Tt]rue|[Ff]alse|1|0',
        'parse': lambda v: v == 'true' or v == 'True' or v == '1'
    }
    String = r'[^,]+?'

    compiled = False

    @classmethod
    def pre_compile(cls):
        cls.compiled = True
        meths = filter(lambda f: hasattr(f, 'filter_data'), cls.__dict__.values())
        if len(meths) == 0:
            return
        cls.runnable_method = meths[0]
        filter_data = cls.runnable_method.filter_data
        cls.async_filter = filter_data['async']
        cls.compile_regex(filter_data)

    @classmethod
    def compile_regex(cls, filter_data):
        params = filter_data['params']
        regexes = []
        parsers = []
        for f in params:
            val = (type(f) == dict) and (f['regex'], f['parse']) or (f, None)
            regexes.append(val[0])
            parsers.append(val[1])

        cls.parsers = parsers
        cls.regex_str = r'%s\(\s*(%s)\s*\)' % (filter_data['name'], r')\s*,\s*('.join(regexes))
        cls.regex = re.compile(cls.regex_str)

    @classmethod
    def init_if_valid(cls, param):
        instance = cls(param)
        if instance.params is not None:
            return instance
        else:
            return None

    def __init__(self, params):
        params = self.regex.match(params) if self.regex else None
        if params:
            params = [parser(param) if parser else param for parser, param in zip(self.parsers, params.groups())]
        self.params = params

    def run(self, callback = None):
        if self.params is not None:
            if self.async_filter:
                self.runnable_method(callback, *self.params)
            else:
                ret = self.runnable_method(*self.params)
                if callback:
                    callback()
                return ret 
